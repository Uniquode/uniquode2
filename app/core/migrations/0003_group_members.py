# -*- coding: utf-8 -*-
import csv

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

from core.utils import fixtures

UserModel = get_user_model()


def group_info(func):
    user_groups = fixtures.initial_fixture_file('user_groups.csv')
    with open(user_groups, 'r') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            users = row['users'].split('|')
            func(row['group'], *users)


# noinspection PyUnusedLocal
def forwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    def add_to_group(group_name, *usernames):
        group = Group.objects.get(name=group_name)
        for username in usernames:
            user = UserModel.objects.get(username=username)
            group.user_set.add(user)

    group_info(add_to_group)


# noinspection PyUnusedLocal
def backwards(apps: StateApps, schema_editor: DatabaseSchemaEditor):

    userset = set()

    def remove_memberships(group_name, *usernames):
        group = Group.objects.get(name=group_name)
        group.user_set.clear()
        # noinspection PyShadowingNames
        for username in usernames:
            userset.add(username)

    group_info(remove_memberships)
    for username in userset:
        user: User
        user = UserModel.objects.get(username=username)
        user.groups.clear()


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('core', '0002_users_groups'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards)
    ]
