# -*- coding: utf-8 -*-
from django.conf import settings


__all__ = (
    'fontawesome',
)


# noinspection PyUnusedLocal
def fontawesome(request):
    fontawesome_version = getattr(settings, 'FONTAWESOME', 'fontawesome-free')

    return {'FONTAWESOME': fontawesome_version}
