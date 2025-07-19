from django.http.request import HttpRequest


def get_remote_addr(request: HttpRequest):
    # remote_addr = request.META.get("HTTP_X_REAL_IP") or request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
    return request.META.get("REMOTE_ADDR")