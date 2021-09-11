# -*- coding: utf-8 -*-
from pathlib import Path

from django.conf import settings


def fixture_path() -> Path:
    # try our custom project base first
    path = getattr(settings, 'PROJECT_ROOT', None)
    if path is None:
        # else fallback to default
        path = getattr(settings, 'BASE_DIR', None)
        if path is None:
            raise ValueError("I can't find any base directory for fixtures")
    return Path(path) / 'fixtures'


def fixture_file(filename: str) -> Path:
    return fixture_path() / filename


def initial_fixtures_path() -> Path:
    return fixture_file('initial')


def initial_fixture_file(filename: str) -> Path:
    return initial_fixtures_path() / filename
