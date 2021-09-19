# -*- coding: utf-8 -*-
"""
This module is for use of standalone scripts only
"""
from django_env import Env
import django


def configure_settings(env=None):
    if env is None:
        env = Env(readenv=True, parents=True)

    env.setdefault('DJANGO_SETTINGS_MODULE', 'conf')

    django.setup()
