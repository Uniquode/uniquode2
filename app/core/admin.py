# -*- coding: utf-8 -*-
from django.conf import settings


if settings.ADMIN_ENABLED:
    from django.contrib import admin

    from .models import Icon, Category, Message

    admin.site.register(Icon)
    admin.site.register(Category)
    admin.site.register(Message)
