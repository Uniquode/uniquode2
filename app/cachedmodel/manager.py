# -*- coding: utf-8 -*-
from django.db import models
from django.utils.functional import empty

from .utils.lazymodel import model_cache_key, OBJECT_DOES_NOT_EXIST, get_model_cache
from .utils.modelutils import (
    lookup_cache_key,
    model_cache_deleted_cache_key,
    model_row_cache_enabled,
    save_lookup_cache_key,
    GET_ARGS_PK_KEY,
)
DOES_NOT_EXIST_CACHE_TIMEOUT = 60 * 5
DELETED_CACHE_TIMEOUT = 60
LOOKUP_CACHE_TIMEOUT = 60 * 60


class RelatedFieldManager(models.Manager):

    use_for_related_fields = True

    def using(self, *args, **kwargs):
        """
        Returns a QuerySet using the selected database.

        This will also override the QuerySet's "get" method to use the
        manager's "get" method instead, taking advantage of caching. This
        only applies to the first, top-level QuerySet; filtering it will
        clone the queryset and then not having caching applied.

        The purpose of this hack is to apply caching to ForeignKeyField
        properties, which end up using this method to get related values.

        """

        queryset = self.get_queryset().using(*args, **kwargs)
        manager = self

        # noinspection PyShadowingNames
        def get(*args, **kwargs):
            return manager.get(*args, **kwargs)

        queryset.get = get
        return queryset


def _only_item(dict_: dict) -> tuple:
    if len(dict_) == 1:
        for key, value in dict_.items():
            return key, value
    return empty, empty


class CachedGetManager(RelatedFieldManager):
    """
    Manager for caching results of the get() method. Uses an ordinary
    dictionary by default, but can be overridden to use anything that
    supports dictionary-like access, such as a memcache wrapper.

    """

    cache_backend = {}

    def get(self, *args, **kwargs):
        if not args:
            key, value = _only_item(kwargs)
            if key in GET_ARGS_PK_KEY:
                pk = value
                try:
                    result = self.cache_backend[pk]
                except KeyError:
                    result = super(CachedGetManager, self).get(*args, **kwargs)
                    self.cache_backend[pk] = result
                return result
        return super(CachedGetManager, self).get(*args, **kwargs)


class RowCacheManager(RelatedFieldManager):
    """
    Manager for caching single-row queries. To make invalidation easy,
    we use an extra layer of indirection. The query arguments are used as a
    cache key, whose stored value is the object pk, from which the final pk
    cache key can be generated. When a model using RowCacheManager is saved,
    this pk cache key should be invalidated. Doing two memcached queries is
    still much faster than fetching from the database.

    """

    # noinspection PyProtectedMember
    def get(self, *args, **kwargs):

        if not model_row_cache_enabled():
            # Bypass the cache.
            return super(RowCacheManager, self).get(*args, **kwargs)

        cache, timeout = get_model_cache()

        object_pk = None
        # to avoid UnboundError
        model_cache_deleted_key = None

        key, value = _only_item(kwargs)
        if key in GET_ARGS_PK_KEY:
            # Generate the cache key directly, since we have the id/pk.
            pk_key = model_cache_key(self.model, value)
            lookup_key = None
        else:
            # This lookup is not simply an id/pk lookup.
            # Get the cache key for this lookup.

            # Handle related managers, which automatically use core_filters
            # to filter querysets using the related object's ID.
            core_filters = getattr(self, 'core_filters', None)
            if isinstance(core_filters, dict):
                # Combine the core filters and the kwargs because that is what
                # the related manager will do when building the queryset.
                lookup_kwargs = dict(core_filters)
                lookup_kwargs.update(kwargs)
            else:
                lookup_kwargs = kwargs

            lookup_key = lookup_cache_key(self.model, **lookup_kwargs)

            # Try to get the cached pk_key.
            object_pk = cache.get(lookup_key)
            pk_key = object_pk and model_cache_key(self.model, object_pk)

            # Check if this object was changed within the last minute
            model_cache_deleted_key = object_pk and model_cache_deleted_cache_key(self.model, object_pk)

        # Try to get a cached result if the pk_key is known.
        result = None
        if pk_key and pk_key in cache:
            result = cache.get(pk_key)

        # in case we recorded the miss
        if result == OBJECT_DOES_NOT_EXIST or object_pk == OBJECT_DOES_NOT_EXIST:
            raise self.model.DoesNotExist

        if not result:
            try:
                # The result was not in cache, so fetch it from the database
                result = super(RowCacheManager, self).get(*args, **kwargs)
            except self.model.DoesNotExist as e:
                # Shall we cache DoesNotExist? Because this is risky depending on who calls it we are going to
                # whitelist the models that we want to cache for and that we know cause unnecessary db calls
                if getattr(self.model, 'cache_for_does_not_exist', False):
                    if model_cache_deleted_key and cache.get(model_cache_deleted_key, False):
                        cache_timeout = 60
                    else:
                        cache_timeout = DOES_NOT_EXIST_CACHE_TIMEOUT
                    if lookup_key:
                        cache.set(lookup_key, OBJECT_DOES_NOT_EXIST, timeout=cache_timeout)
                    else:
                        cache.set(pk_key, OBJECT_DOES_NOT_EXIST, timeout=cache_timeout)
                raise e

            object_pk = result.pk

            # And cache the result against the pk_key for next time.
            pk_key = model_cache_key(result, object_pk)
            cache.set(pk_key, result, timeout=timeout)

            # If a lookup was used, then cache the pk against it. Next time
            # the same lookup is requested, it will find the relevant pk and
            # be able to get the cached object using that.
            if lookup_key:
                if model_cache_deleted_key and cache.get(model_cache_deleted_key, False):
                    # If the objects is changed recently, there is a high possibility that slave db hasn't synced yet.
                    # So we only cache it for 60s instead of an hour to reduce the error.
                    # We only need to do this for lookup_key because pk_key cache was refreshed when the object
                    # is updated. By this way, it read from master db and ensured the value is up to date.
                    cache.set(lookup_key, object_pk, DELETED_CACHE_TIMEOUT)
                else:
                    cache.set(lookup_key, object_pk, timeout=LOOKUP_CACHE_TIMEOUT)

                save_lookup_cache_key(self.model, object_pk, lookup_key)

        return result
