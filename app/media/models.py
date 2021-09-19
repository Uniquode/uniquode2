# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from cachedmodel.models import CachedModel


class Icon(CachedModel):
    name = models.CharField(_('Icon Name'), max_length=64, blank=False, null=False, unique=True)
    svg = models.TextField(_('SVG'))
    tags = TaggableManager(_('Tags'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']