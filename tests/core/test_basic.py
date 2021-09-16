# -*- coding: utf-8 -*-
from http import HTTPStatus as status

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_page(client, settings):
    if not settings.ADMIN_ENABLED:
        pytest.skip('Django admin is disabled')
    else:
        # reliable url in this app
        response = client.get(reverse('admin:index'), follow=True)
        assert response.status_code == int(status.OK)


@pytest.mark.django_db
def test_ping(client):
    response = client.get(reverse('ping'), follow=True)
    assert response.status_code == int(status.OK)
    resp_json = response.json()
    assert isinstance(resp_json, dict)
    assert 'message' in resp_json
    assert resp_json['message'] == 'pong'

