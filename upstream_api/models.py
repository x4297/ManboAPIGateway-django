from datetime import  datetime

from django.db import models
from django.contrib.auth.models import User


class AppClient(models.Model):
    appid = models.CharField(max_length=36, db_index=True)
    secret = models.CharField(max_length=256)
    user = models.OneToOneField(User, models.CASCADE)


class UPUser(models.Model):
    username = models.CharField(max_length=128)
    note = models.CharField(max_length=128)
    parent_path = models.CharField(max_length=256)
    is_enable = models.BooleanField()


class ApiLog(models.Model):
    method = models.CharField(max_length=16)
    host = models.CharField(max_length=256)
    path = models.CharField(max_length=2048)
    status_code = models.IntegerField(db_index=True)
    operator = models.CharField(max_length=128, null=True)
    remote_addr = models.GenericIPAddressField(protocol="IPv4")
    keyword = models.CharField(max_length=256, null=True)
    date_time = models.DateTimeField(default=datetime.now, db_index=True)
    result = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
