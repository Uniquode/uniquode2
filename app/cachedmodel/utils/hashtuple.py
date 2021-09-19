# -*- coding: utf-8 -*-
import inspect
import hashlib

from django.utils.encoding import force_str, smart_bytes

__all__ = (
    'HashableTuple',
)

class HashableTuple(tuple):

    def __new__(cls, *items):
        return tuple.__new__(cls, cls._create_sequence(items))

    @classmethod
    def _create_one(cls, item):
        if isinstance(item, cls):
            return item
        elif isinstance(item, (list, tuple, set)):
            return tuple(cls._create_sequence(*item))
        if isinstance(item, dict):
            return tuple((cls._create_one(key), cls._create_one(value)) for (key, value) in sorted(item.items()))
        elif inspect.isclass(item) or inspect.isfunction(item) or inspect.ismethod(item):
            return item.__name__
        elif isinstance(item, (int, str)):
            return force_str(item)
        else:
            return item

    @classmethod
    def _create_sequence(cls, *items):
        for item in items:
            yield cls._create_one(item)

    @property
    def hash(self):
        return hashlib.sha256(smart_bytes(repr(self))).hexdigest()
