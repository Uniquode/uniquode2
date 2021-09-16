# -*- coding: utf-8 -*-
from django.db.models.signals import ModelSignal


removed_from_cache = ModelSignal(use_caching=True)
