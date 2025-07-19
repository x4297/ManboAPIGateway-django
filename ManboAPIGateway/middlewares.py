from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from upstream_api.models import ApiLog
from .private_settings import ADMIN_WHITE_LABEL, API_WHITE_LABEL
from .utils import get_remote_addr


class LogMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # api log
        if not request.path.startswith("/api/"):
            response = self.get_response(request)
            return response

        request.custom_data = {
            "operator": None,
            "user": None,
            "keyword": None
        }

        response = self.get_response(request)
        request.get_full_path()
        ApiLog(
            method=request.method[:2048],
            host=request.get_host()[:256],
            path=request.path[:2048],
            status_code=response.status_code,
            operator=request.custom_data.get("operator"),
            remote_addr=get_remote_addr(request),
            keyword=request.custom_data.get("keyword"),
            result=response.text[:2048],
            user=request.custom_data.get("user")
        ).save()

        return response


class AdminWhiteLabelMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # admin access control
        if request.path.startswith("/admin/") and get_remote_addr(request) not in ADMIN_WHITE_LABEL:
            return HttpResponseForbidden("ip not allow")

        # api access control
        if request.path.startswith("/api/") and get_remote_addr(request) not in API_WHITE_LABEL:
            return HttpResponseForbidden("ip not allow")

        return self.get_response(request)
