from rest_framework import views, status
from rest_framework.request import Request
from rest_framework.utils.serializer_helpers import ReturnList

from .models import UPUser
from .serializers import SearchUPUsersByPrefixSerializer, UPUserSerializer, EnableUPUserSerializer, ChangPhoneSerializer
from .synchronize import enable_user, get_user_detail, change_phone
from .response import Response


class SearchUPUsersByPrefix(views.APIView):
    throttle_scope = "search"

    def post(self, request: Request, format=None) -> Response:
        request.custom_data["user"] = request.user
        input_serializer = SearchUPUsersByPrefixSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(code=1, status=status.HTTP_400_BAD_REQUEST, message=input_serializer.errors)
        
        username_prefix = input_serializer.validated_data.get("username_prefix")
        query_set = UPUser.objects.filter(username__startswith=username_prefix)[:6]
        request.custom_data["operator"] = input_serializer.validated_data.get("operator")
        request.custom_data["keyword"] = username_prefix

        if query_set.count() > 5:
            return Response(code=2, status=status.HTTP_400_BAD_REQUEST, message="查询结果多于5个，请联系管理员操作")

        up_user = UPUserSerializer(query_set, many=True)  # type: ignore
        user_list: ReturnList = up_user.data  # type: ignore

        for user in user_list:  # get phone number. update status, note
            user: dict
            try:
                r = get_user_detail(user["username"])
                if r["code"] != 0:
                    if r["code"] == -10:  # user not exists. Do not synchronize local database
                        user_list.remove(user)
                    else:
                        Response(code=4, status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="原始接口调用异常-查询账号详细信息")
                else:
                    phone: str = r["result"]["phone"]
                    if len(phone) != 0:
                        user["phone"] = r["result"]["phone"][:3] + "****" + r["result"]["phone"][-4:]
                    else:
                        user["phone"] = ""
                    # update status
                    user["note"] = r["result"]["note"]
                    user["is_enable"] = True if r["result"]["is_enable"] else False
            except:
                Response(code=4, status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="原始接口调用异常-查询账号详细信息")

        return Response(code=0, message="success", data=user_list or [])


class EnableUPUser(views.APIView):
    throttle_scope = "change"

    def post(self, request: Request, format=None) -> Response:
        request.custom_data["user"] = request.user
        input_serializer = EnableUPUserSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(code=1, status=status.HTTP_400_BAD_REQUEST, message=input_serializer.errors)

        username = input_serializer.validated_data.get("username")
        query_set = UPUser.objects.filter(username=username)
        request.custom_data["operator"] = input_serializer.validated_data.get("operator")
        request.custom_data["keyword"] = username

        if len(query_set) != 1:
            return Response(code=3, status=status.HTTP_400_BAD_REQUEST, message="用户查询结果数量不等于1")

        try:  # do not judge if user is enabled
            enable_user(username)
        except Exception as e:
            return Response(code=4, status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="原始接口调用异常-启用账号")

        query_set[0].is_enable = True
        query_set[0].save()

        return Response(code=0, message="success")


class ChangePhone(views.APIView):
    throttle_scope = "change"

    def post(self, request: Request, format=None) -> Response:
        request.custom_data["user"] = request.user
        input_serializer = ChangPhoneSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(code=1, status=status.HTTP_400_BAD_REQUEST, message=input_serializer.errors)

        username = input_serializer.validated_data.get("username")
        phone = input_serializer.validated_data.get("phone")

        query_set = UPUser.objects.filter(username=username)
        request.custom_data["operator"] = input_serializer.validated_data.get("operator")
        request.custom_data["keyword"] = username + " - " + phone

        if len(query_set) != 1:
            return Response(code=3, status=status.HTTP_400_BAD_REQUEST, message="用户查询结果数量不等于1")

        try:
            change_phone(query_set.first(), phone)  # type: ignore
        except Exception as e:
            return Response(code=4, status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="原始接口调用异常-修改电话号码")

        query_set[0].save()

        return Response(code=0, message="success")
