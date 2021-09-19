# -*- coding: utf-8 -*-
"""
This module if a settings facade that injects itself between client code
and the Django settings module so that certain variables can be evaluated
dynamically and on-depend inset of set in stone at applicatino startup.
"""
from django.conf import LazySettings
from components import site_info

# save original
__getattr__ = LazySettings.__getattr__


class LazySettingsExt(LazySettings):
    """ Define a version of LazySettings with enhanced __getattr__ """

    def __getattr__(self, name: str):

        site_id = getattr(site_info, 'site_id', None)

        value = None
        if name == 'SITE_ID':
            value = site_id

        if value is not None:
            return value

        # Fall back to the settings defined in our codebase.
        return __getattr__(self, name)


LazySettings.__getattr__ = LazySettingsExt.__getattr__
