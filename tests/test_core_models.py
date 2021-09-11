# -*- coding: utf-8 -*-
import pytest
from django.contrib.auth import get_user_model

from core.models import Icon, Category, Message

UserModel = get_user_model()


@pytest.mark.django_db
def test_model_icon():
    icon, _ = Icon.objects.get_or_create(name='one', defaults=dict(svg=''))
    assert icon.name == 'one'
    assert icon.svg == ''
    assert icon.dt_created
    assert icon.dt_modified


@pytest.mark.django_db
def test_model_category():
    icon, _ = Icon.objects.get_or_create(name='one', defaults=dict(svg=''))
    category, _ = Category.objects.get_or_create(name='one', defaults=dict(icon=icon))
    assert category.name == 'one'
    assert category.icon.name == 'one'
    assert category.dt_created
    assert category.dt_modified


@pytest.mark.django_db
def test_model_message():
    user, _ = UserModel.objects.get_or_create(username='test')
    message = Message.objects.create(
        to=user,
        name='Sending User',
        email='my@email.com',
        topic='Testing message',
        text='''Hello Test,

This is a test

Regards,
Sending
''')
    saved_id = message.id

    def check_message(user):
        assert message.id == saved_id
        assert message.to == user
        assert message.name == 'Sending User'
        assert message.email == 'my@email.com'
        assert message.topic == 'Testing message'

        return Message.objects.get(id=saved_id)

    message = check_message(user)
    message = check_message(user)

    message.to = None
    message.save()

    message = check_message(None)
