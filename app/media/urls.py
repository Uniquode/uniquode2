# -*- coding: utf-8 -*-
from django.contrib.flatpages import views
from django.urls import path

from . import views

urlpatterns = [
    path('icon/<slug:name>', views.icon, name='icon'),
]
