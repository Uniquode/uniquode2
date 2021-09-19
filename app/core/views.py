# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponsePermanentRedirect, HttpRequest
from django.views import View
from django.views.generic import FormView

from components.view_mixins import MarkdownPage, PrevPageMixin, TemplateSitetreeView
from .forms import MessageForm

__all__ = (
    'HomeView',
    'AboutView',
    'MessagesView',
    'LoginView',
    'LogoutView',
    'favicon',
    'ping'
)


def favicon(request):
    from django.templatetags.static import static
    return HttpResponsePermanentRedirect(static('core/images/favicon.ico'),)


def ping(request):
    return JsonResponse({'message': 'pong'})


class HomeView(MarkdownPage):
    pass


class AboutView(MarkdownPage):
    pass


class MessagesView(FormView, MarkdownPage, PrevPageMixin):
    """
    Requires the following html in the page to pop out the contact form:
    <button type="button" class="primary" title="Contact Form" aria-label="Contact Form">
      <label for="modal-control-contact"><i class="fas fa-user"></i></label>
    </button>
    """
    template_name = 'core/markdownpage-contact.html'
    form_class = MessageForm
    commento = True

    def post(self, request: HttpRequest, *args, **kwargs):
        self.set_success_url(request)
        # type: MessageForm
        form = self.get_form()
        if form.is_valid():
            # noinspection PyUnresolvedReferences
            form.instance.created_by = request.user
            if form.save():
                messages.info(self.request, 'Message sent')
                return self.form_valid(form)
        # post messages for all errors
        for field, error in form._errors.items():
            messages.error(self.request, f'{field}: {error}')
        return self.form_invalid(form)


class UnderConstructionView(TemplateSitetreeView):
    template_name = 'core/under-construction.html'


class ArticlesView(UnderConstructionView):
    pass


class NewsView(UnderConstructionView):
    pass


class TestView(LoginRequiredMixin, MarkdownPage):
    pass


class LoginView(FormView, PrevPageMixin):
    http_method_names = ['post', 'put']
    # use form class from django.contrib.auth to handle the authorisation
    form_class = AuthenticationForm

    def post(self, request: HttpRequest, *args, **kwargs):
        self.set_success_url(request)
        form = self.get_form()
        if form.is_valid():
            login(request, form.get_user())
            messages.info(request, 'You have signed in.')
            return self.form_valid(form)
        messages.error(request, 'Authentication failed.')
        return self.previous_page(request)


class LogoutView(View, PrevPageMixin):
    http_method_names = ['get']

    def get(self, request: HttpRequest, *args, **kwargs):
        self.set_success_url(request)
        logout(request)
        messages.warning(request, 'You have signed out.')
        return self.previous_page(request)
