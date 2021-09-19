# -*- coding: utf-8 -*-
from django.http import JsonResponse, HttpResponse

from media.models import Icon


def icon(request, name):
    from typing import Union
    icon: Union[Icon, None] = None
    for key in ('name', 'pk'):
        try:
            get_by = {key: name}
            icon = Icon.objects.filter(**get_by).first()
            break
        except Icon.DoesNotExist:
            continue
    else:
        return JsonResponse(
            data=dict(errors=[f"icon {name} does not exist"]),
            status=404
        )

    image = icon.svg.encode('utf8')
    return HttpResponse(content=image,
                        headers={'content-disposition': f"{icon.name}.svg"},
                        content_type='image/svg'
    )