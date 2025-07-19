import json
from datetime import datetime

from django.db import transaction
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.models import User
import httpx

from ManboAPIGateway.private_settings import UPAPI_NETLOC
from .models import UPUser
from .signature import signature
from .exceptions import EnableUPUserException, ChangePhoneException


def enable_user(username: str) -> None:
    url_enable_user = f"{UPAPI_NETLOC}/Api.php?controller=User&action=ExtSetUserEnable"
    parameters = {
        "username": username,
        "enable": 1,
        "timestamp": int(datetime.now().timestamp())
    }

    sig_params = parameters.copy()
    sig_params.update({"controller": "User", "action": "ExtSetUserEnable"})

    parameters["apitoken"] = signature(sig_params)

    r = httpx.post(url_enable_user, data=parameters, verify=False, timeout=httpx.Timeout(30))
    r = json.loads(r.text)
    if r["code"] != 0 or r["success"] is not True:
        raise EnableUPUserException()


def change_phone(up_user: UPUser, phone: str):
    # change phone
    url = f"{UPAPI_NETLOC}/Api.php?controller=User&action=UpdateUserCloud"
    parameters = {
        "old_name": up_user.username,
        "new_name": up_user.username,
        "parent_group": up_user.parent_path,
        "timestamp": int(datetime.now().timestamp()),
        "phone": phone
    }

    sig_params = parameters.copy()
    sig_params.update({"controller": "User", "action": "UpdateUserCloud"})
    parameters["apitoken"] = signature(sig_params)
    r = httpx.post(url, data=parameters, verify=False, timeout=httpx.Timeout(30))
    r = json.loads(r.text)
    if r["code"] != 0 or r["success"] is not True:
        raise ChangePhoneException()

    # synchronize in cluster
    url = f"{UPAPI_NETLOC}/Api.php?controller=Updater&action=DataSyncCloud"
    parameters: dict = {
        "timestamp": int(datetime.now().timestamp())
    }

    sig_params = parameters.copy()
    sig_params.update({"controller": "Updater", "action": "DataSyncCloud"})
    parameters["apitoken"] = signature(sig_params)
    r = httpx.post(url, data=parameters, verify=False, timeout=httpx.Timeout(30))
    r = json.loads(r.text)
    if r["code"] != 0 or r["success"] is not True:
        raise ChangePhoneException()


def get_user_detail(username: str) -> dict:
    url = f"{UPAPI_NETLOC}/Api.php?controller=User&action=ExGetUserInfo"
    parameters: dict = {
        "timestamp": int(datetime.now().timestamp()),
        "username": username,
    }

    sig_params = parameters.copy()
    sig_params.update({"controller": "User", "action": "ExGetUserInfo"})
    parameters["apitoken"] = signature(sig_params)

    return httpx.post(url, data=parameters, verify=False, timeout=httpx.Timeout(10)).json()


def get_users() -> httpx.Response:
    url = f"{UPAPI_NETLOC}/Api.php?controller=User&action=GetSearchData"
    parameters: dict = {
        "timestamp": int(datetime.now().timestamp()),
        "offset": 0,
        "limit": 10000
    }

    sig_params = parameters.copy()
    sig_params.update({"controller": "User", "action": "GetSearchData"})
    parameters["apitoken"] = signature(sig_params)

    return httpx.post(url, data=parameters, verify=False, timeout=httpx.Timeout(60))


@transaction.atomic
def synchronize() -> None:
    user = User.objects.get(username="system")
    query_set = User.objects.filter(username="system")
    failed_msg = ""

    try:
        r = get_users().json()
        failed_msg = r
        r = r["result"]["data"]

        UPUser.objects.all().delete()

        for i in r:
            UPUser(
                username = i["name"],
                note = i["note"],
                parent_path = i["parent_path"],
                is_enable = True if i["is_enable"] else False
            ).save()

        LogEntry.objects.log_actions(
            user_id=user.pk,
            queryset=query_set,
            action_flag=ADDITION,
            change_message="UP user synchronize success: " + failed_msg
        )
    except Exception:
        LogEntry.objects.log_actions(
            user_id=user.pk,
            queryset=query_set,
            action_flag=ADDITION,
            change_message="UP user synchronize failed"
        )
