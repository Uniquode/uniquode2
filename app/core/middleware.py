# -*- coding: utf-8 -*-
"""
This extends django.contrib.site.middleware.CurrentSiteMiddleware to
also saves the site_id in an async local
"""
from django.contrib.sites.middleware import CurrentSiteMiddleware

from components.site_info import site_info


class CoreMiddleware(CurrentSiteMiddleware):

    def process_request(self, request):
        super().process_request(request)
        setattr(site_info, 'site_id', request.site.id)
