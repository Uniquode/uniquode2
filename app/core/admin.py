# -*- coding: utf-8 -*-
from django.conf import settings

if settings.ADMIN_ENABLED:
    from django.contrib import admin
    from django.utils.safestring import mark_safe, SafeString

    from .components.admin import TaggedAdminMixin, TimestampAdminMixin, CreatedByAdminMixin
    from .models import Icon, Category, Message

    class ModelAdminMixin:

        class Media:
            css = {
                'all': ('css/site/site-admin.css',)
            }

    class CategoryAdmin(ModelAdminMixin, admin.ModelAdmin):
        search_fields = ('name',)

    admin.site.register(Category, CategoryAdmin)

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

    # noinspection PyMethodMayBeStatic
    class MessagesAdmin(CreatedByAdminMixin, TimestampAdminMixin, admin.ModelAdmin):
        list_display = ('id', 'since_created', 'created_by', 'message_name', 'message_email', 'topic')
        actions = None
        fieldsets = [
            (None, {
                'fields': [
                    ('to', 'name', 'email',)
                ]
            }
             ),
            ("Content", {
                'fields': [
                    ('topic', 'text')
                ]
            }
             ),
        ]
        search_fields = [
            'name', 'email', 'topic',
            'created_by__first_name', 'created_by__last_name',
            'created_by__email',
        ]
        list_filter = ('created_by',)

        def message_name(self, obj):
            return f'{obj.created_by.first_name} {obj.created_by.last_name}' if obj.created_by else obj.name

        def message_email(self, obj):
            return f'{obj.created_by.email}' if obj.created_by else obj.email

    admin.site.register(Message, MessagesAdmin)
