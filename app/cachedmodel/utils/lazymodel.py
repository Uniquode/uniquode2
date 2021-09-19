# -*- coding: utf-8 -*-
import logging
from typing import Union

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import BaseCache, caches
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DatabaseError
from django.utils.functional import SimpleLazyObject, empty

from .modelutils import get_identifier

__all__ = (
    'LazyModelObject',
    'LazyModelObjectDict',
    'LazyModelObjectError',
    'get_model_cache',
    'model_cache_key',
    'OBJECT_DOES_NOT_EXIST',
)


OBJECT_DOES_NOT_EXIST = 'object-does-not-exists'


class LazyModelObjectError(ValueError):

    def __init__(self, *args, exc=None):
        self._exc = exc
        super().__init__(*args)

    @property
    def exc(self):
        return self._exc


def get_model_cache(name: Union[None, str] = None) -> (BaseCache, int):
    if not hasattr(get_model_cache, 'cache'):
        get_model_cache.cache = getattr(settings, 'MODEL_ROW_CACHE', 'default')
        get_model_cache.cache_timeout = int(getattr(settings, 'MODEL_ROW_CACHE_TIMEOUT', 60 * 60 * 24 * 7))
    return caches[name or get_model_cache.cache], get_model_cache.cache_timeout


def model_cache_key(instance, pk=None) -> str:
    identifier = get_identifier(instance, pk=pk)
    return f'CachedModel:{identifier}'


def unpickle_lazy_object(obj, args, kwargs):
    return LazyModelObject(obj, *args, **kwargs)


class LazyModelObject(SimpleLazyObject):
    """
    A lazy wrapper for a database object, with caching.

    The cache layer uses the same cache keys as ModelWithCaching,
    and both rely on the same signal handlers for invalidation.

    Raises a LazyModelObjectError (subclass of ValueError) if fail_silently=False.

    """

    def __init__(self, object_or_string, *args, **kwargs):
        super(LazyModelObject, self).__init__(self._get_cached_instance)
        self.__dict__['_fail_silently'] = kwargs.pop('fail_silently', True)
        self.__dict__['_init_args'] = (object_or_string, args, kwargs)

    @classmethod
    def get_uninitialized_value(cls):
        from django.utils.functional import empty
        return empty

    @classmethod
    def get_not_found_value(cls):
        return None

    def __bool__(self):
        if self._wrapped is empty:
            self._setup()
        return bool(self._wrapped)

    def __reduce_ex__(self, proto):
        """
        Allow lazy model instances to be pickled.

        The cache backend will not retained;
        the default backend will be used when the object is unpickled.

        """

        (object_or_string, args, kwargs) = self._init_args

        # If a model was used to initialize this object, then swap it out for
        # its identifier string. The resulting data will be much smaller.
        if isinstance(object_or_string, models.Model):
            object_or_string = self.get_identifier(object_or_string)

        return unpickle_lazy_object, (object_or_string, args, kwargs)

    def _get_cached_instance(self):
        """
        A cache wrapper around _get_instance, using the same cache keys
        as the row-level cache.
        """

        try:
            identifier = self._get_identifier()
        except (ValueError, ObjectDoesNotExist) as error:
            if self._fail_silently:
                return None
            raise LazyModelObjectError(exc=error) from error

        # Get the cache key, basically just namespacing the identifier
        cache_key = model_cache_key(identifier)

        cache, timeout = self._cache
        cace: BaseCache
        if cache_key in cache:
            instance = cache.get(cache_key)
        else:
            instance = self._get_instance(identifier)
            cache.set(cache_key, instance, timeout=timeout)

        if instance is None and not self._fail_silently:
            raise LazyModelObjectError(f'{identifier} not found.')
        return instance

    def _get_identifier(self):
        """Get the identifier string for the represented object."""

        if '_identifier' not in self.__dict__:

            object_or_string, args, kwargs = self._init_args

            # Get the identifier for the wrapped object, e.g. 'auth.user.1234'
            # If there is a lookup in the kwargs, then the following call
            # will figure out the object_pk. It caches these lookups.
            kwargs['_fail_silently'] = self._fail_silently
            self.__dict__['_identifier'] = get_identifier(object_or_string, *args, **kwargs)

        return self.__dict__['_identifier']

    @staticmethod
    def _get_instance(identifier):
        """Get the object from the database."""
        # noinspection PyBroadException
        try:
            app_label, model, object_pk = identifier.split('.', maxsplit=2)
            # we don't expect to find anything, so don't log
            if object_pk != 'None':
                if object_pk == OBJECT_DOES_NOT_EXIST:
                    raise ObjectDoesNotExist()
                content_type = ContentType.objects.get_by_natural_key(app_label, model)
                return content_type.get_object_for_this_type(pk=object_pk)
        except ContentType.DoesNotExist:
            logging.warning(f'Could not find content type for {identifier!r}')
        except ObjectDoesNotExist:
            logging.warning(f'Could not find related object for {identifier!r}')
        except DatabaseError:   # don't mask these
            raise
        except Exception:
            logging.exception(f'Could not get related object for {identifier!r}', log_function=logging.error)

    @classmethod
    def get_identifier(cls, *args, **kwargs):
        if args and type(args[0]) is cls:
            # Handle instances of this class differently.
            # noinspection PyProtectedMember
            object_or_string, args, kwargs = args[0]._init_args
            args = [object_or_string] + list(args)
        return get_identifier(*args, **kwargs)

    @classmethod
    def get_model_class(cls, *args, **kwargs):
        identifier = cls.get_identifier(*args, **kwargs)
        app_label, model, object_pk = identifier.split('.', 2)
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        return content_type.model_class()

    @property
    def object_pk(self):
        """The object pk value as a string."""

        if self._wrapped not in (None, empty):
            return str(self._wrapped.pk)

        if '_object_pk' in self.__dict__:
            return self.__dict__['_object_pk']

        identifier = self._get_identifier()
        if identifier:
            # noinspection PyBroadException
            try:
                object_pk = identifier.split('.', 2)[-1]
                if object_pk == 'None':
                    object_pk = None
                self.__dict__['_object_pk'] = object_pk
                return object_pk
            except Exception:
                pass

        raise AttributeError()

    def __repr__(self):
        return f'<LazyModelObject: {self._get_identifier()}>'


class LazyModelObjectDict(dict):
    """
    A dictionary of LazyModelObject instances. Use this to avoid duplicate
    database/cache lookups and having duplicate model instances in memory.

    """

    def get_or_add(self, *args, **kwargs):
        """
        Get or add a LazyModelObject instance to this dictionary. Accepts the same
        arguments as the LazyModelObject class. Returns a LazyModelObject instance.

        Note: this will evaluate LazyModelObject instances when adding new ones.

        Usage:
            items = LazyModelObjectDict()
            user = items.get_or_add(User, 123)

        """

        key = LazyModelObject.get_identifier(*args, **kwargs)
        try:
            return self[key]
        except KeyError:
            item = LazyModelObject(*args, **kwargs)
            if not item:
                item = None
            self[key] = item
            return item
