# -*- coding: utf-8 -*-
import random

from django.conf import settings


# noinspection PyMethodMayBeStatic
class DBRouter:

    # noinspection PyAttributeOutsideInit
    def readonly_db(self):
        if not hasattr(self, '_readonly_db_list'):
            """cache this"""
            choices = list()
            for db_label, db_settings in settings.DATABASES.items():
                options = db_settings.get('OPTIONS', {})
                if any(ro_flag in options for ro_flag in ('READONLY', 'READ_ONLY')):
                    choices.append(db_label)
            self._readonly_db_list = choices
        if self._readonly_db_list:
            return random.choice(self._readonly_db_list)
        return 'default'

    def db_for_read(self, model, **hints):
        return self.readonly_db()

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migrations on default
        """
        return db == 'default'
