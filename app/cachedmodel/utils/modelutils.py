# -*- coding: utf-8 -*-
import functools
import json
import logging
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.contenttypes.models import ContentType

from .hashtuple import HashableTuple

__all__ = (
    'get_identifier_string',
    'get_object_pk',
    'model_row_cache_enabled',
    'model_cache_deleted_cache_key',
    'lookup_cache_key',
    'lookup_cache_master_key',
    'save_lookup_cache_key',
    'GET_ARGS_PK_KEY',
)


GET_ARGS_PK_KEY = ('id', 'id__exact', 'pk', 'pk__exact')
IDENTIFIER_REGEX = re.compile(r"^[\w\d_]+\.[\w\d_]+\.[\w\d-]+$")
TRUTH_VALUES = ('y', 'Y', '1', 't', 'T', 'en', 'on')


@functools.cache
def model_row_cache_enabled() -> bool:
    enabled = getattr(settings, 'MODEL_ROW_CACHE_ENABLED', True)
    return any(enabled.startswith(x) for x in TRUTH_VALUES) if isinstance(enabled, str) else enabled


def model_cache_deleted_cache_key(obj, pk=None) -> str:
    identifier = get_identifier(obj, pk=pk)
    return f"ModelDeletedCache:{identifier})"


def lookup_cache_master_key(instance, pk=None) -> str:
    identifier = get_identifier(instance, pk)
    return f"ModelCacheLookupMaster:{identifier}"


def save_lookup_cache_key(instance, object_pk, lookup_key, lookup_timeout=None):
    from .lazymodel import get_model_cache
    # save lookup cache key to purge them all when needed
    identifier = get_identifier(instance, object_pk)
    # noinspection PyTypeChecker
    master_key = lookup_cache_master_key(identifier)
    cache, timeout = get_model_cache()
    list_lookup_cache_keys = []
    if master_key in cache:
        cache_keys = cache.get(master_key)
        if cache_keys:
            list_lookup_cache_keys = json.loads(cache_keys)

    if lookup_key not in list_lookup_cache_keys:
        list_lookup_cache_keys.append(lookup_key)
        cache.set(master_key, json.dumps(list_lookup_cache_keys), timeout=lookup_timeout or timeout)


def get_model_name(instance) -> str:
    """return the full model name of an object in app_label.model_class format"""
    # noinspection PyProtectedMember
    opts = instance._meta
    return f"{opts.app_label}.{opts.model_name}"


def get_model_by_ct(instance):
    if isinstance(instance, ContentType):
        return instance.model_class()
    return instance


def get_identifier_string(instance, pk):
    return f'{get_model_name(instance)}.{str(pk).replace(" ", "")}'


def get_identifier(instance, pk=None, _fail_silently=True, **kwargs) -> str:
    """
    Get an unique identifier for the provided object
    Unless overridden, returns <app_label>.<object_name>.<pk>.
    """
    if isinstance(instance, str):
        """just return if it is an identifier"""
        if not IDENTIFIER_REGEX.match(instance):
            if not _fail_silently:
                logging.debug(f"Provided string '{instance}' is not a valid identifier.")
            return ''
        return instance

    model = get_model_by_ct(instance)

    if pk is None:
        if kwargs:
            for key, value in kwargs.items():
                if key in GET_ARGS_PK_KEY:
                    pk = value
                    break
            else:
                pk = get_object_pk(model, _fail_silently=_fail_silently, **kwargs)

        elif isinstance(model, models.Model):
            # noinspection PyProtectedMember
            pk = model._get_pk_val()

    return get_identifier_string(model, pk)


def lookup_cache_key(model, *args, **kwargs):
    identifier = get_identifier(model, HashableTuple(args, kwargs).hash)
    return f"ModelCacheLookup:{identifier}"


def get_object_pk(model: models.Model, _fail_silently=True, **kwargs):
    from .lazymodel import get_model_cache

    cache_key = lookup_cache_key(model, **kwargs)
    cache, timeout = get_model_cache()
    if cache_key in cache:
        object_pk = cache[cache_key]
    else:
        from ..models import CachedModel
        try:
            object_pk = model.objects.get(**kwargs).pk
            cache.set(cache_key, object_pk, timeout=timeout)

            # if model is CachedModel, this lookup cache key should be saved in model.objects.get(**kwargs).pk
            if not isinstance(model, CachedModel):
                save_lookup_cache_key(model, object_pk, cache_key)

        except (model.DoesNotExist, ObjectDoesNotExist):
            if not _fail_silently:
                raise
            object_pk = None

    return object_pk
