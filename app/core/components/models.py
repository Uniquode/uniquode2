# -*- coding: utf-8 -*-
"""
Some useful model building blocks
All models are are abstract, so don't need to be within an app
"""
from django.contrib.auth import get_user_model
from django.db import models

__all__ = (
    'TimestampModelMixin',
    'AuthorModelMixin',
    'ActivatedModelMixin',
    'get_sentinel_user'
)


UserModel = get_user_model()

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class TimestampModelMixin(models.Model):
    """
    Abstract model with auto-timestamps
    """
    dt_created = models.DateTimeField('Created', auto_now_add=True, editable=False)
    dt_modified = models.DateTimeField('Modified', auto_now=True, editable=False)

    class Meta:
        abstract = True


class AuthorModelMixin(models.Model):
    created_by = models.ForeignKey(get_user_model(), editable=False, blank=True, null=True, related_name='+',
                                   on_delete=models.SET(get_sentinel_user))

    class Meta:
        abstract = True


class ActivatedModelMixin(models.Model):
    is_active = models.BooleanField(default=False)

    def activate(self, state: bool = True, save: bool = True):
        if self.is_active is state:
            raise ValueError(f"{self.__class__.__name__}: Already {'' if state else 'in'}activated")
        self.is_active = state
        if save:
            self.save()

    def deactivate(self, state: bool = False, save: bool = True):
        self.activate(state, save)

    class Meta:
        abstract = True
