# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history import register as history_register, models as history_models
from taggit.managers import TaggableManager

from .components.models import TimestampModel, AuthorModel

UserModel = get_user_model()


# register history on our user table here
history_register(UserModel, app='core')


# some of the primitive model blocks
class Message(TimestampModel, AuthorModel):
    to = models.ForeignKey(UserModel, blank=True, null=True, related_name='+',
                           on_delete=models.SET_NULL)
    name = models.CharField(_('Name'), max_length=64, blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=64, blank=True, null=True)
    topic = models.CharField(_('Topic'), max_length=255, blank=False)
    text = models.TextField(_('Message'))

    def __str__(self):
        bits = [
            f'Id:{self.id}',
            f'From<{self.name}>',
        ]
        if self.to:
            bits.append(f'To<{self.to}>')
        bits.append(f'Re<{self.topic}>')
        return ' '.join(bits)


class Icon(TimestampModel):
    name = models.CharField(_('Icon Name'), max_length=64, blank=False, null=False, unique=True)
    svg = models.TextField(_('SVG'))
    tags = TaggableManager(_('Tags'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(TimestampModel):
    name = models.CharField(_('Category Name'), max_length=64, blank=False, null=False)
    icon = models.ForeignKey(Icon, to_field='name', null=True, related_name='+',
                             on_delete=models.SET_NULL)
    history = history_models.HistoricalRecords(_('History'))
    tags = TaggableManager(_('Tags'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
