#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import (and export) font-awesome icons
"""
import argparse
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def setting(var: str, default=None):
    return getattr(settings, var, default)


def node_modules():
    nmdir = setting('YARN_ROOT_PATH', setting('NPM_ROOT_PATH'))
    if not nmdir:
        raise ImproperlyConfigured("You must set one of YARN_ROOT_PATH or NPM_ROOT_PATH")
    return Path(nmdir) / 'node_modules'


ICONSETS = ('fontawesome-pro', 'fontawesome-free')
ICONSTYLES = ('duotone', 'solid', 'regular', 'light', 'brands')


def font_awesome_icons(stats):

    icons_seen = set()
    for fontset in ICONSETS:
        base = node_modules() / '@fortawesome' / fontset
        if base.exists() and base.is_dir():
            base /= 'svgs'
            for style in ICONSTYLES:
                svg_base = base / style
                if svg_base.exists() and svg_base.is_dir():
                    for svg in svg_base.glob('*.svg'):
                        if svg.name in icons_seen:
                            stats['dupes'] += 1
                            stats[style] += 0
                        else:
                            stats['total'] += 1
                            stats[style] += 1
                            yield svg
                        icons_seen.add(svg.name)


def attach_tags(stats):
    from core.utils.fixtures import initial_fixture_file
    from django.utils.text import slugify
    from taggit.models import Tag
    from media.models import Icon

    import json

    icon_tags = initial_fixture_file('icon_tags.json')
    if not icon_tags.exists():
        return

    with icon_tags.open() as fp:
        tags_json = json.load(fp)

    for record in tags_json:
        if all(key in record for key in ('name', 'tags')):
            try:
                icon = Icon.objects.get(name=record['name'])
            except Icon.DoesNotExist:
                continue

            tags = record['tags']
            for tag_name in tags:
                Tag.objects.get_or_create(name=tag_name, defaults={"slug": slugify(tag_name)})
            qs = Tag.objects.filter(name__in=tags)
            icon.tags.add(*qs)


LABELS = {
    'created': 'New Icons Imported',
    'dupes':   'Duplicates Skipped',
    'total':   'Non-Duplicates',
}


def main(args: argparse.Namespace):
    stats = defaultdict(int)

    if args.action == 'clear':
        from media.models import Icon
        from django.contrib.contenttypes.models import ContentType
        from taggit.models import TaggedItem

        ct = ContentType.objects.get(app_label='core', model='icon')
        TaggedItem.objects.filter(content_type=ct).delete()

        Icon.objects.all().delete()

    elif args.action == 'import':
        from media.models import Icon

        for label in LABELS.keys():
            stats[label] = 0

        for svgpath in font_awesome_icons(stats):
            content = svgpath.read_text()
            icon_name = svgpath.name[:-(len(svgpath.suffix))]
            icon, created = Icon.objects.get_or_create(name=icon_name, defaults=dict(svg=content))
            if created:
                stats['created'] += 1
            else:
                icon.svg = content
                icon.save()

        attach_tags(stats)

    else:
        raise NotImplementedError(args.action)

    if stats:
        for statistic, value in stats.items():
            try:
                label = LABELS[statistic]
            except KeyError:
                label = f"Style: {statistic}"
            print(f"{label:20}: {value:6d}")


if __name__ == '__main__':
    import sys
    cwd = Path.cwd().resolve()
    if cwd not in sys.path:
        sys.path.append(str(cwd))

    try:
        from core.utils.configure import configure_settings
    except ImportError:
        raise EnvironmentError('This script must be run from the Django application directory')

    configure_settings()

    prog = Path(sys.argv[0]).resolve()
    parser = argparse.ArgumentParser(prog=prog.name, description=__doc__)
    parser.add_argument('action', type=str, action='store', choices=('import', 'export', 'clear'))

    main(parser.parse_args())
