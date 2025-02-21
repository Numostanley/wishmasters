import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class AllowedHostCheckerMiddleWare(MiddlewareMixin):

    def process_request(self, request):  # noqa
        data = {
            'message': 'Stay Off'
        }
        try:
            if request.META.get('HTTP_HOST', '') not in settings.ALLOWED_HOSTS:
                return JsonResponse(
                    status=444, data=data
                )
            pass
        except Exception as e:
            logging.error('AllowedHostCheckerMiddleWare.get@Error')
            logging.error(e)
            return JsonResponse(
                status=200, data=data
            )
