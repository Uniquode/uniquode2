# -*- coding: utf-8 -*-
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'core'

    # noinspection PyUnresolvedReferences
    from . import settings
