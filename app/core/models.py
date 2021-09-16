# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager

from .cachedmodel.models import CachedModel
from .components.models import TimestampModelMixin, AuthorModelMixin

UserModel = get_user_model()


# some of the primitive model blocks
class Message(CachedModel, TimestampModelMixin, AuthorModelMixin):
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


class Icon(CachedModel):
    name = models.CharField(_('Icon Name'), max_length=64, blank=False, null=False, unique=True)
    svg = models.TextField(_('SVG'))
    tags = TaggableManager(_('Tags'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(CachedModel):
    name = models.CharField(_('Category Name'), max_length=64, blank=False, null=False)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    icon = models.ForeignKey(Icon, to_field='name', null=True, related_name='+',
                             on_delete=models.SET_NULL)
    tags = TaggableManager(_('Tags'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Page(TimestampModelMixin, AuthorModelMixin):
    """
    Base document record
    """
    label = models.CharField(_('Title'), max_length=64, db_index=True)
    content = MarkdownxField(_('Content'))

    def __str__(self):
        return self.label
