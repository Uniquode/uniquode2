# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin


if settings.ADMIN_ENABLED:
    from categories.models import Category

    class CategoryAdmin(admin.ModelAdmin):
        search_fields = ('name',)

    admin.site.register(Category, CategoryAdmin)

