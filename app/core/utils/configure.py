# -*- coding: utf-8 -*-
"""
This module is for use of standalone scripts only
"""
from django_env import Env

Env(readenv=True, parents=True).setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')


def configure_settings():
    import django

    django.setup()
    pass
