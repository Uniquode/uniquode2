# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path('favicon.ico', views.favicon, name='favicon'),
    path('ping/', views.ping, name='ping'),
]