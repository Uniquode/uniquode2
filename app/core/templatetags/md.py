# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
import markdown as md


register = template.Library()

markdown_extensions = settings.MARKDOWNX_MARKDOWN_EXTENSIONS
markdown_extension_configs = settings.MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS


@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=markdown_extensions, extension_configs=markdown_extension_configs)
