# -*- coding: utf-8 -*-
from django.conf import settings

if settings.ADMIN_ENABLED:
    from django.contrib import admin

    from components.admin import TimestampAdminMixin, CreatedByAdminMixin
    from markdownx.admin import MarkdownxModelAdmin
    from .models import Message, Page

    class ModelAdminMixin:

        class Media:
            css = {
                'all': ('css/site/site-admin.css',)
            }

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


    class PageAdmin(CreatedByAdminMixin, TimestampAdminMixin, MarkdownxModelAdmin):
        list_display = ('label', 'since_created', 'since_modified')
        actions = None
        fieldsets = [
            (None, {
                'fields': [
                    ('label', 'content')
                ]
            }),
        ]
        readonly_fields = ('dt_created', 'dt_modified')


    admin.site.register(Page, PageAdmin)
