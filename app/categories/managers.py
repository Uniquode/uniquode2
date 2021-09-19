# -*- coding: utf-8 -*-
import uuid
from operator import attrgetter

from django.contrib.contenttypes.models import ContentType
from django.db import models, router, connections
from django.db.models import signals
from taggit.models import CommonGenericTaggedItemBase, GenericUUIDTaggedItemBase


# noinspection PyProtectedMember
class CategoryManager(models.Manager):

    def __init__(self, through, model, instance, prefetch_cache_name):
        super().__init__()
        self.through = through
        self.model = model
        self.instance = instance
        self.prefetch_cache_name = prefetch_cache_name

    def is_cached(self, instance):
        return self.prefetch_cache_name in instance._prefetched_objects_cache

    def get_queryset(self, extra_filters=None):
        try:
            return self.instance._prefetched_objects_cache[self.prefetch_cache_name]
        except (AttributeError, KeyError):
            kwargs = extra_filters if extra_filters else {}
            return self.through.tags_for(self.model, self.instance, **kwargs)

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is not None:
            raise ValueError("Custom queryset can't be used for this lookup.")

        instance = instances[0]
        db = self._db or router.db_for_read(type(instance), instance=instance)

        fieldname = (
            "object_id"
            if issubclass(self.through, CommonGenericTaggedItemBase)
            else "content_object"
        )
        fk = self.through._meta.get_field(fieldname)
        query = {
            f"{self.through.tag_relname()}__{fk.name}__in": {
                obj._get_pk_val() for obj in instances
            }
        }
        join_table = self.through._meta.db_table
        source_col = fk.column
        connection = connections[db]
        qn = connection.ops.quote_name
        qs = (
            self.get_queryset(query)
                .using(db)
                .extra(
                select={
                    "_prefetch_related_val": "{}.{}".format(
                        qn(join_table), qn(source_col)
                    )
                }
            )
        )

        if issubclass(self.through, GenericUUIDTaggedItemBase):

            def uuid_rel_obj_attr(v):
                value = attrgetter("_prefetch_related_val")(v)
                if value is not None and not isinstance(value, uuid.UUID):
                    input_form = "int" if isinstance(value, int) else "hex"
                    value = uuid.UUID(**{input_form: value})
                return value

            rel_obj_attr = uuid_rel_obj_attr
        else:
            rel_obj_attr = attrgetter("_prefetch_related_val")

        return (
            qs,
            rel_obj_attr,
            lambda obj: obj._get_pk_val(),
            False,
            self.prefetch_cache_name,
            False,
        )

    def _lookup_kwargs(self):
        return self.through.lookup_kwargs(self.instance)

    def add(self, *categories, through_defaults=None, cat_kwargs=None, **kwargs):

        if cat_kwargs is None:
            cat_kwargs = {}
        db = router.db_for_write(self.through, instance=self.instance)

        cat_objs = self._to_tag_model_instances(categories, cat_kwargs)
        new_ids = {t.pk for t in cat_objs}

        vals = (
            self.through._default_manager.using(db)
                .values_list("category_id", flat=True)
                .filter(**self._lookup_kwargs())
        )

        new_ids = new_ids - set(vals)

        signals.m2m_changed.send(
            sender=self.through,
            action="pre_add",
            instance=self.instance,
            reverse=False,
            model=self.through.category_model(),
            pk_set=new_ids,
            using=db,
        )

        for tag in cat_objs:
            self.through._default_manager.using(db).get_or_create(
                tag=tag, **self._lookup_kwargs(), defaults=through_defaults
            )

        signals.m2m_changed.send(
            sender=self.through,
            action="post_add",
            instance=self.instance,
            reverse=False,
            model=self.through.tag_model(),
            pk_set=new_ids,
            using=db,
        )

    def _to_category_model_instances(self, categories, cat_kwargs):
        """
        Takes an iterable containing either strings, tag objects, or a mixture
        of both and returns set of tag objects.
        """
        db = router.db_for_write(self.through, instance=self.instance)

        str_tags = set()
        cat_objs = set()

        for t in categories:
            if isinstance(t, self.through.category_model()):
                cat_objs.add(t)
            elif isinstance(t, str):
                str_tags.add(t)
            else:
                raise ValueError(
                    f"Cannot add {t} ({type(t)}). Expected {type(self.through.category_model())} or str."
                )

        manager = self.through.category_model()._default_manager.using(db)

        existing = manager.filter(name__in=str_tags, **cat_kwargs)

        categories_to_create = str_tags - set(c.name for c in existing)

        cat_objs.update(existing)

        for new_categories in categories_to_create:
            lookup = {"name": new_categories, **cat_kwargs}

            tag, create = manager.get_or_create(**lookup, defaults={"name": new_categories})
            cat_objs.add(tag)

        return cat_objs

    def names(self):
        return self.get_queryset().values_list("name", flat=True)

    def slugs(self):
        return self.get_queryset().values_list("slug", flat=True)

    def set(self, *categories, through_defaults=None, **kwargs):
        """
        Set the object's tags to the given n tags. If the clear kwarg is True
        then all existing tags are removed (using `.clear()`) and the new tags
        added. Otherwise, only those tags that are not present in the args are
        removed and any new tags added.

        Any kwarg apart from 'clear' will be passed when adding tags.

        """
        db = router.db_for_write(self.through, instance=self.instance)

        clear = kwargs.pop("clear", False)
        cat_kwargs = kwargs.pop("cat_kwargs", {})

        if clear:
            self.clear()
            self.add(*categories, **kwargs)
        else:
            # make sure we're working with a collection of a uniform type
            objs = self._to_category_model_instances(categories, cat_kwargs)

            # get the existing tag strings
            old_tag_strs = set(
                self.through._default_manager.using(db)
                    .filter(**self._lookup_kwargs())
                    .values_list("category__name", flat=True)
            )

            new_objs = []
            for obj in objs:
                if obj.name in old_tag_strs:
                    old_tag_strs.remove(obj.name)
                else:
                    new_objs.append(obj)

            self.remove(*old_tag_strs)
            self.add(*new_objs, through_defaults=through_defaults, **kwargs)

    def remove(self, *categories):
        if not categories:
            return

        db = router.db_for_write(self.through, instance=self.instance)

        qs = (
            self.through._default_manager.using(db)
                .filter(**self._lookup_kwargs())
                .filter(category__name__in=categories)
        )

        old_ids = set(qs.values_list("category_id", flat=True))

        signals.m2m_changed.send(
            sender=self.through,
            action="pre_remove",
            instance=self.instance,
            reverse=False,
            model=self.through.category_model(),
            pk_set=old_ids,
            using=db,
        )
        qs.delete()
        signals.m2m_changed.send(
            sender=self.through,
            action="post_remove",
            instance=self.instance,
            reverse=False,
            model=self.through.category_model(),
            pk_set=old_ids,
            using=db,
        )

    def clear(self):
        db = router.db_for_write(self.through, instance=self.instance)

        signals.m2m_changed.send(
            sender=self.through,
            action="pre_clear",
            instance=self.instance,
            reverse=False,
            model=self.through.category_model(),
            pk_set=None,
            using=db,
        )

        self.through._default_manager.using(db).filter(**self._lookup_kwargs()).delete()

        signals.m2m_changed.send(
            sender=self.through,
            action="post_clear",
            instance=self.instance,
            reverse=False,
            model=self.through.category_model(),
            pk_set=None,
            using=db,
        )

    def most_common(self, min_count=None, extra_filters=None):
        queryset = (
            self.get_queryset(extra_filters)
                .annotate(num_times=models.Count(self.through.tag_relname()))
                .order_by("-num_times")
        )
        if min_count:
            queryset = queryset.filter(num_times__gte=min_count)

        return queryset

    def similar_objects(self):
        lookup_kwargs = self._lookup_kwargs()
        lookup_keys = sorted(lookup_kwargs)
        qs = self.through.objects.values(*lookup_kwargs.keys())
        qs = qs.annotate(n=models.Count("pk"))
        qs = qs.exclude(**lookup_kwargs)
        qs = qs.filter(category__in=self.all())
        qs = qs.order_by("-n")

        items = {}
        if len(lookup_keys) == 1:
            # Can we do this without a second query by using a select_related()
            # somehow?
            f = self.through._meta.get_field(lookup_keys[0])
            remote_field = f.remote_field
            rel_model = remote_field.model
            objs = rel_model._default_manager.filter(
                **{
                    f"{remote_field.field_name}__in": [r["content_object"] for r in qs]
                }
            )
            actual_remote_field_name = f.target_field.get_attname()
            for obj in objs:
                items[(getattr(obj, actual_remote_field_name),)] = obj
        else:
            preload = {}
            for result in qs:
                preload.setdefault(result["content_type"], set())
                preload[result["content_type"]].add(result["object_id"])

            for ct, obj_ids in preload.items():
                ct = ContentType.objects.get_for_id(ct)
                for obj in ct.model_class()._default_manager.filter(pk__in=obj_ids):
                    items[(ct.pk, obj.pk)] = obj

        results = []
        for result in qs:
            obj = items[tuple(result[k] for k in lookup_keys)]
            obj.similar_tags = result["n"]
            results.append(obj)
        return results
