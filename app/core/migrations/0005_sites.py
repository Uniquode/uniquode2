# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db import migrations, DatabaseError
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


# noinspection PyUnusedLocal
def forwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):
    # create a default site
    default_site = {'domain': 'example.com', 'name': 'Default default site'}
    try:
        Site.objects.create(pk=1, **default_site)
    except DatabaseError:
        Site.objects.filter(pk=1).update(**default_site)


# noinspection PyUnusedLocal
def backwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    Site.objects.all().delete()


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('core', '0004_group_permissions'),
        ('sites', '0002_alter_domain_unique'),
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards)
    ]
