# -*- coding: utf-8 -*-
from django.urls import path, include

from . import views

urlpatterns = [
    path('favicon.ico', views.favicon, name='favicon'),
    # Web UI
    path('login/', views.LoginView.as_view(), name='signin'),
    path('logout/', views.LogoutView.as_view(), name='signout'),

    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.MessagesView.as_view(), name='contact'),

    path('markdownx/', include('markdownx.urls')),


    # API
    path('api/ping/', views.ping, name='ping'),
]