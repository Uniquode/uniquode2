# -*- coding: utf-8 -*-
from django.utils.timesince import timesince


class CreatedByAdminMixin:

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        # noinspection PyUnresolvedReferences
        super().save_model(request, obj, form, change)


# noinspection PyMethodMayBeStatic
class TimestampAdminMixin:

    def since_created(self, obj):
        return timesince(obj.dt_created)

    def since_modified(self, obj):
        return timesince(obj.dt_created)


class TaggedAdminMixin:

    # noinspection PyUnresolvedReferences
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def _tags(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
