# -*- coding: utf-8 -*-
"""
csv helper functions for use in migrations
"""
import csv

from .fixtures import initial_fixture_file, fixture_file


def process_csv(apps, func, modelname, filename, keyfield, related_fields=None, initial=True):
    # label.model
    app_label, modelname = modelname.rsplit('.', maxsplit=1)
    model = apps.get_model(app_label, modelname, require_ready=True)
    relations = {}
    for field, modelname in (related_fields or {}).items():
        # label.model.field
        app_label, modelname, to = modelname.rsplit('.', maxsplit=2)
        related_model = apps.get_model(app_label, modelname, require_ready=True)
        relations.update({field: (related_model, to)})

    fixture_path = initial_fixture_file if initial else fixture_file
    with fixture_path(filename).open('r', encoding='utf-8') as fp:
        csv_reader = csv.DictReader(fp)
        for row in csv_reader:
            for field, (related_model, to) in relations.items():
                row[field] = related_model.get(to=row[field])
            func(model, row, keyfield)


def process_import(apps, modelname, filename, keyfield, related_fields=None, initial=True):

    # noinspection PyUnusedLocal,PyShadowingNames
    def create_record(model, row, keyfield=None):
        # filter the empty values, leave them to default value
        row = {k: v for k, v in row.items() if v}
        model.objects.create(**row)

    process_csv(apps, create_record, modelname, filename, keyfield, related_fields, initial)


# noinspection PyUnusedLocal
def process_remove(apps, modelname, filename, keyfield, related_fields=None, initial=True):

    # noinspection PyShadowingNames
    def remove_record(model, row, keyfield=None):
        # extract the username
        keyfields = keyfield if isinstance(keyfield, (list, tuple)) else [keyfield]
        row = {key: row[key] for key in keyfields}
        try:
            model.objects.get(**row).delete()
        except model.DoesNotExist:
            return  # simply do nothing

    process_csv(apps, remove_record, modelname, filename, keyfield)
