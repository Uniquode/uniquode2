# -*- coding: utf-8 -*-
import json

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import related_descriptors
from django.db.models.signals import pre_delete, post_delete, post_save, m2m_changed

from . import signals
from .lib.lazymodel import get_model_cache, model_cache_key
from .lib.modelutils import get_identifier_string, lookup_cache_master_key
from .manager import RowCacheManager

DEFAULT_MANAGER_NAME = 'objects'
BASE_MANAGER_NAME = '_related'


class MetaCaching(ModelBase):
    """
    Sets ``objects'' on any model that inherits from ModelWithCaching to be a RowCacheManager.
    This is tightly coupled to Django internals, so it could (and did) break if you upgrade Django.
    This was done partially as a proof-of-concept.

    Django now stores managers in the model._meta (class Options) attribute and cannot be set
    directly at the class level.

    """

    # noinspection PyMethodParameters
    def __new__(cls, name, bases, attrs, default_manager_name=None, base_manager_name=None, **kwargs):
        new_class = ModelBase.__new__(cls, name, bases, attrs, **kwargs)
        # noinspection PyProtectedMember
        opts = new_class._meta

        def add_manager(manager_name, attr_base):

            if not hasattr(new_class, manager_name):
                # Attach a new manager.
                manager = RowCacheManager()
                manager.name = manager_name
                manager.model = opts.model
                manager.contribute_to_class(new_class, manager_name)
                opts.managers_map[manager_name] = manager
            else:
                manager = getattr(new_class, manager_name)
                try:
                    # if required, insert RowCacheManager into manager bases first in MRO
                    # note that this cannot work if manager.__class__.__base__ == object
                    # see https://stackoverflow.com/questions/3193158/bases-doesnt-work-whats-next/3193260
                    if manager.__class__ != RowCacheManager and RowCacheManager not in manager.__class__.__bases__:  # noqa
                        manager.__class__.__bases__ = (RowCacheManager,) + manager.__class__.__bases__
                except TypeError:
                    pass
            if manager not in opts.local_managers:
                opts.local_managers.append(manager)
            setattr(opts, attr_base, manager)
            setattr(opts, f"{attr_base}_name", manager_name)

        add_manager(default_manager_name or DEFAULT_MANAGER_NAME, 'default_manager')
        add_manager(base_manager_name or BASE_MANAGER_NAME, 'base_manager')
        return new_class


class CachedModel(models.Model, metaclass=MetaCaching):

    class Meta:
        default_manager_name = DEFAULT_MANAGER_NAME
        base_manager_name = BASE_MANAGER_NAME
        abstract = True


def create_manager(func, superclass, rel, *args):
    manager_cls = func(superclass, rel, *args)
    if issubclass(rel.model, CachedModel) and not issubclass(manager_cls, RowCacheManager):
        manager_cls = type(manager_cls.__name__, (RowCacheManager,) + manager_cls.__bases__, {})
    return manager_cls


# fixups for manager creators
original_create_forward_many_to_many_manager = related_descriptors.create_forward_many_to_many_manager
original_create_reverse_many_to_one_manager = related_descriptors.create_reverse_many_to_one_manager


def create_forward_many_to_many_manager(superclass, rel, reverse):
    return create_manager(original_create_forward_many_to_many_manager, superclass, rel, reverse)


def create_reverse_many_to_one_manager(superclass, rel):
    return create_manager(original_create_reverse_many_to_one_manager, superclass, rel)


# noinspection PyUnusedLocal
def remove_object_from_cache(sender, instance, **kwargs):

    model = instance.__class__
    instance_pk = instance.pk

    if isinstance(instance, ContentType):
        # The model cache key stuff has special handling to allow passing
        # in a content type instead of the model. At this point though, we are
        # actually working with the content type itself and not the model it
        # represents. So we need to bypass that special handling code.

        instance = get_identifier_string(instance, instance.pk)

    cache, timeout = get_model_cache()

    cache_key = model_cache_key(instance, instance_pk)
    cache.delete(cache_key)

    try:
        # reset cache with new data from master DB
        model.objects.get(id=instance_pk)
    except model.DoesNotExist:
        pass

    # and remove lookup cache keys
    master_key = lookup_cache_master_key(instance, instance_pk)
    if master_key in cache:
        list_lookup_cache_keys = json.loads(cache.get(master_key))
        for key in list_lookup_cache_keys:
            cache.delete(key)
        cache.delete(master_key)

    # Tell anyone else who may be interested that cache was cleaned of instance
    signals.removed_from_cache.send(sender=sender, instance=instance, **kwargs)


pre_delete.connect(remove_object_from_cache)
post_delete.connect(remove_object_from_cache)
post_save.connect(remove_object_from_cache)
m2m_changed.connect(remove_object_from_cache)

related_descriptors.create_forward_many_to_many_manager = create_forward_many_to_many_manager
related_descriptors.create_reverse_many_to_one_manager = create_reverse_many_to_one_manager
