#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

def run():
    import core
    from core.utils.fixtures import initial_fixtures_path

    source_migrations_path = initial_fixtures_path() / 'migrations'
    core_migrations_path = Path(core.__file__).resolve().parent / 'migrations'

    MIGRATION_RE = re.compile(r'(?P<m_id>\d{4})_(?P<m_title>[^ ]+)\.py$')
    AUTH_MIGRATION_RE = re.compile(r'(?P<m_id>\d{2})_(?P<m_title>[^ ]+)\.py$')
    DEPENDENCY_SUB = re.compile(r"^(?P<lead>\s+\('core', ')(?P<migration>\d{4}_\w+)(?P<end>'\),\s*)$", re.MULTILINE)


    def migration_filter(path: Path) -> bool:
        match = MIGRATION_RE.match(path.name)
        return bool(match)


    def auth_migration_filter(path: Path) -> bool:
        match = AUTH_MIGRATION_RE.match(path.name)
        return bool(match)


    migration_files = sorted([path for path in core_migrations_path.glob('*') if migration_filter(path)])
    migrations_to_add = sorted([path for path in source_migrations_path.glob('*') if auth_migration_filter(path)])

    if not migration_files:
        raise ValueError('Need at least 1 existing migration file before data migrations can be added')
    last_migration = migration_files[-1]
    match = MIGRATION_RE.match(last_migration.name)
    start_counter = int(match.groupdict()['m_id'])

    # Allow this to be repeatable, check against existing migrations
    # Title matching is crude but should work
    # Exclude any auth migrations that are already present
    proposed_migrations = {}
    # extract title from each migration
    for migration in migrations_to_add:
        match = AUTH_MIGRATION_RE.match(migration.name)
        title = match.groupdict()['m_title']
        proposed_migrations[title] = migration

    # remove any migrations via matching title that already exists
    for migration in migration_files:
        match = MIGRATION_RE.match(migration.name)
        title = match.groupdict()['m_title']
        try:
            # remove any proposed migration with this title
            migration_name = proposed_migrations[title].name[:-3]
            del proposed_migrations[title]
            print(f"{migration_name} -> skipped: migration already present")
        except KeyError:
            pass

    # Main work loop

    for index, migration in enumerate(proposed_migrations.values(), start=start_counter+1):
        # Read the content of the new migration to install
        content = migration.read_text()

        # Determine the name of the new migration
        match = AUTH_MIGRATION_RE.match(migration.name)
        last_migration_name = last_migration.name[:-3]
        next_migration_name = f"{index:04d}_{match.groupdict()['m_title']}"

        # Make the Path object for the new migration
        next_migration = Path(core_migrations_path) / f"{next_migration_name}.py"

        # substitute the dependency on the most recent migration
        content = DEPENDENCY_SUB.sub(fr'\g<lead>{last_migration_name}\g<end>', content)

        # create and write the migration file with the updated content
        next_migration.write_text(content)
        print(f"{migration.name[:-3]} -> {next_migration_name} [dep {last_migration_name}]")

        last_migration = next_migration

if __name__ == '__main__':
    # ensure we have django settings configured
    import sys

    sys.path.append(str(Path().cwd()))

    from core.utils.configure import configure_settings
    configure_settings()
    run()
