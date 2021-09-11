# -*- coding: utf-8 -*-
import csv

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.db.models import Q

from core.utils import fixtures


def permissions_info(func):
    permission_groups = fixtures.initial_fixture_file('group_permissions.csv')
    with open(permission_groups, 'r') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            permissions = row['permissions'].split('|')
            func(row['app_label'], row['group'], *permissions)


# noinspection PyUnusedLocal
def forwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    def add_group_perms(app_label, group, *permissions):
        group = Group.objects.get(name=group)
        for ct in ContentType.objects.filter(app_label=app_label):
            qs = Q()
            for q in [Q(codename__startswith=perm) for perm in permissions]:
                qs |= q
            qs = Permission.objects.filter(content_type=ct).filter(qs)
            group.permissions.add(*qs)

    permissions_info(add_group_perms)


# noinspection PyUnusedLocal
def backwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    # noinspection PyUnusedLocal
    def remove_group_perms(app_label, group, *permissions):
        group = Group.objects.get(name=group)
        group.permissions.clear()

    permissions_info(remove_group_perms)


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('core', '0005_group_members'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards)
    ]
