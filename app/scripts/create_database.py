#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create or reset the application database
"""
import sys

from django.conf import settings
from django.db import connections
from django.db.backends.postgresql.base import DatabaseWrapper


def execute(db: DatabaseWrapper, sql, ignore_errors=False):
    with db.cursor() as cursor:
        try:
            cursor.execute(sql)
        except Exception as e:
            if ignore_errors:
                print(f"*** {sql} error\n{e}", file=sys.stderr)
                return
            raise


def run():
    default, postgres = settings.DATABASES.get('default', None), settings.DATABASES.get('postgres', None)
    if default and postgres:
        # Create the database with postgres user as the target db spedified in default db
        # may not even exist which causes using that connection to fail
        default_user, default_name = default['USER'], default['NAME']
        postgres_db: DatabaseWrapper = connections['postgres']
        postgres_db.set_autocommit(True)
        print(f"- Possibly dropping existing default database '{default_name}'")
        execute(postgres_db, f'DROP DATABASE IF EXISTS {default_name}')
        print(f"- Creating database '{default_name}' with owner '{default_user}'")
        execute(postgres_db, f'CREATE DATABASE {default_name} WITH OWNER = {default_user}')
        print("* Success")
    else:
        raise ValueError('No SA (postgres) database in Django settings')


if __name__ == '__main__':
    from pathlib import Path
    from argparse import ArgumentParser

    sys.path.append(str(Path.cwd()))
    from core.utils.configure import configure_settings

    configure_settings()

    prog = Path(sys.argv[0])
    parser = ArgumentParser(prog.name, description=__doc__)
    parser.add_argument('init', type=str, choices=('init',), help='Use init to confirm')
    parser.parse_args()
    run()
