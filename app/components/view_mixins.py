# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from sitetree.sitetreeapp import get_sitetree

from core.models import Page


class PrevPageMixin:
    """
    Mixin for handing back to the calling page via modal form
    """
    success_url = reverse_lazy('home')

    def get_success_url(self):
        return self.success_url

    def set_success_url(self, request: HttpRequest, usenext: bool = True):
        if usenext:
            try:
                self.success_url = request.GET['next']
                return
            except KeyError:
                pass
        self.success_url = request.META.get('HTTP_REFERER', self.success_url)

    # noinspection PyUnusedLocal
    def previous_page(self, request):
        return HttpResponseRedirect(self.success_url)


class SiteTreeMixin:
    """
    Tie markdown page content to page sitetree.item
    """
    default_sitetree = "main"       # default

    @property
    def sitetree(self):
        return self.default_sitetree

    def current_sitetree(self, context):
        sitetree = get_sitetree()
        # noinspection PyUnresolvedReferences
        context['request'] = self.request
        sitetree.init_tree(self.sitetree, context)
        return sitetree.get_tree_current_item(self.sitetree)

    def get_page(self, context):
        item = self.current_sitetree(context)
        if item:
            try:
                return Page.objects.get(label__exact=item.url)
            except Page.DoesNotExist:
                pass
        return None


class TemplateSitetreeView(TemplateView, SiteTreeMixin):
    pass


class MarkdownPage(TemplateSitetreeView):
    template_name = 'core/markdownpage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.get_page(context)
        return context
