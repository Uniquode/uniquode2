# -*- coding: utf-8 -*-
from django import forms

from .models import Message

__all__ = (
    'MessageForm',
)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [
            'to',
            'name',
            'email',
            'topic',
            'text'
        ]

    def save(self, commit=True):
        return super().save(commit=True)


