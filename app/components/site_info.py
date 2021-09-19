# -*- coding: utf-8 -*-
from typing import Union

from asgiref.local import Local

__all__ = (
    'site_info',
)

class SiteInfo(Local):

    def __init__(self) -> None:
        super().__init__(thread_critical=False)
        self._site_id = None


site_info = SiteInfo()
