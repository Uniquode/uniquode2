# -*- coding: utf-8 -*-
from django.apps import AppConfig


class CachedModelAppConfig(AppConfig):
    """
    This needs to be registered as an app so that the ready() method
    is run to clear cache entries on database updates.
    """
    name = "core.cachedmodel"
    verbose_name = "Row Cached Models"
