# -*- coding: utf-8 -*-
from django.http import JsonResponse, HttpResponsePermanentRedirect


def favicon(request):
    from django.templatetags.static import static
    return HttpResponsePermanentRedirect(static('core/images/favicon.ico'),)

def ping(request):
    return JsonResponse({'message': 'pong'})
