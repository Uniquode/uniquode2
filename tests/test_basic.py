# -*- coding: utf-8 -*-
from http import HTTPStatus as status


def test_admin_page(client):
    # reliable url in this app
    response = client.get('/admin/', follow=True)
    assert response.status_code == int(status.OK)
