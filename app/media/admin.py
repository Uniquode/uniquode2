# -*- coding: utf-8 -*-
from django.conf import settings


if settings.ADMIN_ENABLED:
    from django.contrib import admin
    from django.utils.safestring import mark_safe, SafeString
    from components.admin import TaggedAdminMixin

    from .models import Icon


    class ModelAdminMixin:

        class Media:
            css = {
                'all': ('css/site/site-admin.css',)
            }

    # noinspection PyMethodMayBeStatic
    class IconAdmin(ModelAdminMixin, admin.ModelAdmin, TaggedAdminMixin):
        list_display = ('_svg', 'name', '_tags')
        search_fields = ('name', 'tags__name', )
        list_filter = ('tags__name',)

        @mark_safe
        def _svg(self, obj) -> SafeString:
            return obj.svg

        class Meta:
            ordering = ['name']

    admin.site.register(Icon, IconAdmin)
