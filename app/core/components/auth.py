# -*- coding: utf-8 -*-
"""
Simplistic authentication overlay using email or username
"""
from django.contrib.auth.backends import ModelBackend, UserModel


class EmailOrUsernameAuthBackend(ModelBackend):
    """
    Override just the authentication method to optionally
    allow login by email if username contains a '@'
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(email=username) if '@' in username \
                else UserModel.objects.get(username=username)
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturnedException):
            # Run the default password hash once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
