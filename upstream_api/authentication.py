from typing import Any

from rest_framework.request import Request
from rest_framework import authentication
from rest_framework import exceptions

from .models import AppClient


class CustomAuthenticatedFailed(exceptions.AuthenticationFailed):
    def __init__(self, detail):
        self.detail = detail


class SignatureAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request: Request) -> tuple[Any, Any]:
        appid = request.data.get("appid", None)
        if not appid:
            raise CustomAuthenticatedFailed(detail={
                "code": 5,
                "success": False,
                "message": "appid为空或错误",
                "result": None
            })
        
        try:
            user = AppClient.objects.get(appid=appid).user
        except Exception as e:
            raise CustomAuthenticatedFailed(detail={
                "code": 6,
                "success": False,
                "message": "appid为空或错误",
                "result": None
            })
        return user, None
