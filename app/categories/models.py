# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from media.models import Icon


class Category(models.Model):
    name = models.CharField(_('Category Name'), max_length=64, unique=True)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    icon = models.ForeignKey(Icon, to_field='name', null=True, related_name='+', on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class CategoryItem(models.Model):
    category = models.ForeignKey(Category, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("content type"),
                                     related_name="%(app_label)s_%(class)s_categories",)
    object_id = models.IntegerField(verbose_name=_("object ID"), db_index=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return _(f"{self.content_object} in category {self.category}")

    @classmethod
    def category_model(cls):
        field = cls._meta.get_field("category")
        return field.remote_field.model

    @classmethod
    def category_relname(cls):
        field = cls._meta.get_field("category")
        return field.remote_field.related_name

    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            "object_id": instance.pk,
            "content_type": ContentType.objects.get_for_model(instance),
        }

    # noinspection PyProtectedMember
    @classmethod
    def categories_for(cls, model, instance=None, **extra_filters):
        category_relname = cls.category_relname()
        model = model._meta.concrete_model
        kwargs = {
            f"{category_relname}__content_type__app_label": model._meta.app_label,
            f"{category_relname}__content_type__model": model._meta.model_name,
        }
        if instance is not None:
            kwargs[f"{category_relname}__object_id"] = instance.pk
        if extra_filters:
            kwargs.update(extra_filters)
        return cls.category_relname().objects.filter(**kwargs).distinct()

    class Meta:
        verbose_name = _("category item")
        verbose_name_plural = _("category items")
        index_together = [["content_type", "object_id"]]
        unique_together = [["content_type", "object_id", "category"]]