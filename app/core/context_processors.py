# -*- coding: utf-8 -*-
from django.conf import settings


__all__ = (
    'fontawesome',
)


# noinspection PyUnusedLocal
def fontawesome(request):
    fontawesome_version = getattr(settings, 'FONTAWESOME', 'fontawesome-free')

    return {'FONTAWESOME': fontawesome_version}


def page_admin_url(request):
    from core.models import Page

    opts = Page._meta
    return {
        'page_admin_url': f"{settings.ADMIN_URL}{opts.app_label}/{opts.model_name}/"
    }
