# -*- coding: utf-8 -*-
import csv

from django.contrib.sites.models import Site
from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


# noinspection PyUnusedLocal
def forwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):
    # create a default site
    Site.objects.get_or_create(pk=1, defaults={'domain': 'example.com', 'name': 'Default default site'})


# noinspection PyUnusedLocal
def backwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    Site.objects.all().delete()


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('core', '0004_group_permissions'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards)
    ]
