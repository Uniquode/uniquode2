# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

from core.utils.migration_csv_helpers import process_import, process_remove


IMPORT_LIST = [
    {
        'modelname': settings.AUTH_USER_MODEL,
        'filename': 'users.csv',
        'keyfield': 'username',
    },
    {
        'modelname': 'auth.Group',
        'filename': 'groups.csv',
        'keyfield': 'name',
    }
]


# noinspection PyUnusedLocal
def forwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):
    for spec in IMPORT_LIST:
        process_import(apps, **spec)


# noinspection PyUnusedLocal
def backwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):
    for spec in reversed(IMPORT_LIST):
        process_remove(apps, **spec)


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards)
    ]
