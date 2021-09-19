# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import ManyToManyRel
from django.db.models.fields.related import RelatedField, lazy_related_operation
from django.db.models.query_utils import PathInfo
from django.utils.translation import gettext_lazy as _

from .managers import CategoryManager
from .models import CategoryItem


class RestrictByContentType:
    """
    An extra restriction used for contenttype restriction in joins.
    """

    contains_aggregate = False

    def __init__(self, alias, col, content_types):
        self.alias = alias
        self.col = col
        self.content_types = content_types

    def as_sql(self, compiler, connection):
        qn = compiler.quote_name_unless_alias
        if len(self.content_types) == 1:
            extra_where = f"{qn(self.alias)}.{qn(self.col)} = %s"
        else:
            extra_where = f"{qn(self.alias)}.{qn(self.col)} IN ({','.join(['%s'] * len(self.content_types))})"
        return extra_where, self.content_types

    def relabel_aliases(self, change_map):
        self.alias = change_map.get(self.alias, self.alias)

    def clone(self):
        return type(self)(self.alias, self.col, self.content_types[:])


# noinspection PyProtectedMember
class CategoryField(RelatedField):
    # Field flags
    many_to_many = True
    many_to_one = False
    one_to_many = False
    one_to_one = False

    _related_name_counter = 0

    def __init__(
            self,
            verbose_name=_("Categories"),
            help_text=_('Selected categories'),
            through=None,
            blank=False,
            related_name=None,
            to=None,
            manager=CategoryManager,
    ):
        self.through = through or CategoryItem
        rel = ManyToManyRel(self, to, related_name=related_name, through=self.through)
        super().__init__(
            verbose_name=verbose_name,
            help_text=help_text,
            blank=blank,
            null=True,
            serialize=False,
            rel=rel,
        )
        self.swappable = False
        self.manager = manager

    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError(
                f"{model.__name__} requires a primary key value before you can access their categories"
            )
        return self.manager(
            through=self.through,
            model=model,
            instance=instance,
            prefetch_cache_name=self.name,
        )

    def deconstruct(self):
        """
        Deconstruct the object, used with migrations.
        """
        name, path, args, kwargs = super().deconstruct()
        # Remove forced kwargs.
        for kwarg in ("serialize", "null"):
            del kwargs[kwarg]
        # Add arguments related to relations.
        rel = self.remote_field
        if isinstance(rel.through, str):
            kwargs["through"] = rel.through
        elif not rel.through._meta.auto_created:
            kwargs["through"] = f"{rel.through._meta.app_label}.{rel.through._meta.object_name}"

        related_model = rel.model
        if isinstance(related_model, str):
            kwargs["to"] = related_model
        else:
            kwargs["to"] = f"{related_model._meta.app_label}.{related_model._meta.object_name}"

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        self.set_attributes_from_name(name)
        self.model = cls
        self.opts = cls._meta

        cls._meta.add_field(self)
        setattr(cls, name, self)
        if not cls._meta.abstract:
            if isinstance(self.remote_field.model, str):

                def resolve_related_class(cls, model, field):
                    field.remote_field.model = model

                lazy_related_operation(
                    resolve_related_class, cls, self.remote_field.model, field=self
                )

            if isinstance(self.through, str):

                def resolve_related_class(cls, model, field):
                    self.through = model
                    self.remote_field.through = model
                    self.post_through_setup(cls)

                lazy_related_operation(
                    resolve_related_class, cls, self.through, field=self
                )

            else:
                self.post_through_setup(cls)

    def get_internal_type(self):
        return "ManyToManyField"

    def post_through_setup(self, cls):
        self.use_gfk = self.through is None or issubclass(self.through, CategoryItem)

        if not self.remote_field.model:
            self.remote_field.model = self.through._meta.get_field(
                "category"
            ).remote_field.model

        if self.use_gfk:
            tagged_items = GenericRelation(self.through)
            tagged_items.contribute_to_class(cls, "categories")

        for rel in cls._meta.local_many_to_many:
            if rel == self or not isinstance(rel, CategoryManager):
                continue
            if rel.through == self.through:
                raise ValueError("You can't have two CategoryManagers with the same through model.")

    def save_form_data(self, instance, value):
        getattr(instance, self.name).set(*value)

    def formfield(self, **kwargs):
        super().formfield(**kwargs)
    # def formfield(self, form_class=CategoryField, **kwargs):
    #     defaults = {
    #         "label": capfirst(self.verbose_name),
    #         "help_text": self.help_text,
    #         "required": not self.blank,
    #     }
    #     defaults.update(kwargs)
    #     return form_class(**defaults)

    def value_from_object(self, obj):
        if obj.pk is None:
            return []
        qs = self.through.objects.select_related("category").filter(
            **self.through.lookup_kwargs(obj)
        )
        return [ti.tag for ti in qs]

    def m2m_reverse_name(self):
        return self.through._meta.get_field("category").column

    def m2m_reverse_field_name(self):
        return self.through._meta.get_field("category").name

    def m2m_target_field_name(self):
        return self.model._meta.pk.name

    def m2m_reverse_target_field_name(self):
        return self.remote_field.model._meta.pk.name

    def m2m_column_name(self):
        if self.use_gfk:
            return self.through._meta.private_fields[0].fk_field
        return self.through._meta.get_field("content_object").column

    def m2m_db_table(self):
        return self.through._meta.db_table

    def bulk_related_objects(self, new_objs, using):
        return []

    def _get_mm_case_path_info(self, direct=False, filtered_relation=None):
        pathinfos = []
        linkfield1 = self.through._meta.get_field("content_object")
        linkfield2 = self.through._meta.get_field(self.m2m_reverse_field_name())
        if direct:
            join1infos = linkfield1.get_reverse_path_info(
                filtered_relation=filtered_relation
            )
            join2infos = linkfield2.get_path_info(
                filtered_relation=filtered_relation
            )
        else:
            join1infos = linkfield2.get_reverse_path_info(
                filtered_relation=filtered_relation
            )
            join2infos = linkfield1.get_path_info(
                filtered_relation=filtered_relation
            )
        pathinfos.extend(join1infos)
        pathinfos.extend(join2infos)
        return pathinfos

    def _get_gfk_case_path_info(self, direct=False, filtered_relation=None):
        pathinfos = []
        from_field = self.model._meta.pk
        opts = self.through._meta
        linkfield = self.through._meta.get_field(self.m2m_reverse_field_name())
        if direct:
            join1infos = [
                PathInfo(
                    self.model._meta,
                    opts,
                    [from_field],
                    self.remote_field,
                    True,
                    False,
                    filtered_relation,
                )
            ]
            join2infos = linkfield.get_path_info(
                filtered_relation=filtered_relation
            )
        else:
            join1infos = linkfield.get_reverse_path_info(
                filtered_relation=filtered_relation
            )
            join2infos = [
                PathInfo(
                    opts,
                    self.model._meta,
                    [from_field],
                    self,
                    True,
                    False,
                    filtered_relation,
                )
            ]
        pathinfos.extend(join1infos)
        pathinfos.extend(join2infos)
        return pathinfos

    def get_path_info(self, filtered_relation=None):
        if self.use_gfk:
            return self._get_gfk_case_path_info(
                direct=True, filtered_relation=filtered_relation
            )
        else:
            return self._get_mm_case_path_info(
                direct=True, filtered_relation=filtered_relation
            )

    def get_reverse_path_info(self, filtered_relation=None):
        if self.use_gfk:
            return self._get_gfk_case_path_info(
                direct=False, filtered_relation=filtered_relation
            )
        else:
            return self._get_mm_case_path_info(
                direct=False, filtered_relation=filtered_relation
            )

    def get_joining_columns(self, reverse_join=False):
        if reverse_join:
            return (self.model._meta.pk.column, "object_id"),
        else:
            return ("object_id", self.model._meta.pk.column),

    def get_extra_restriction(self, where_class, alias, related_alias):
        extra_col = self.through._meta.get_field("content_type").column
        content_type_ids = [
            ContentType.objects.get_for_model(subclass).pk
            for subclass in _get_subclasses(self.model)
        ]
        return RestrictByContentType(related_alias, extra_col, content_type_ids)

    def get_reverse_joining_columns(self):
        return self.get_joining_columns(reverse_join=True)

    @property
    def related_fields(self):
        return [(self.through._meta.get_field("object_id"), self.model._meta.pk)]

    @property
    def foreign_related_fields(self):
        return [self.related_fields[0][1]]


def _get_subclasses(model):
    subclasses = [model]
    for field in model._meta.get_fields():
        if isinstance(field, OneToOneRel) and getattr(
                field.field.remote_field, "parent_link", None
        ):
            subclasses.extend(_get_subclasses(field.related_model))
    return subclasses
