from datetime import datetime, timedelta

from rest_framework import serializers

from .models import UPUser, AppClient
from .signature import signature


class SignatureSerializer(serializers.Serializer):
    operator = serializers.CharField(max_length=128)
    timestamp = serializers.IntegerField(min_value=0)
    nonce = serializers.IntegerField(min_value=0)
    appid = serializers.CharField(min_length=36, max_length=36)
    token = serializers.CharField(min_length=64, max_length=64)

    def validate(self, attrs: dict):
        # check timestamp
        try:
            ts = datetime.fromtimestamp(attrs.get("timestamp"))  # type: ignore
        except Exception:
            raise serializers.ValidationError({"timestamp": ["时间戳格式错误"]})
        if datetime.now() - ts > timedelta(minutes=10):
            raise serializers.ValidationError({"timestamp": ["重放攻击"]})

        # check signature
        params = attrs.copy()
        appid = params["appid"]
        token = params.pop("token")
        secret = AppClient.objects.get(appid=appid).secret

        sig = signature(params, secret)
        if sig != token:
            raise serializers.ValidationError({"token": ["token计算错误"]})

        return attrs


class SearchUPUsersByPrefixSerializer(SignatureSerializer):
    username_prefix = serializers.CharField(max_length=128)


class UPUserSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = UPUser
        fields = ["username", "note", "is_enable"]


class EnableUPUserSerializer(SignatureSerializer):
    username = serializers.CharField(max_length=128)


class UPUserListSerializer(serializers.Serializer):
    total = serializers.IntegerField()


class ChangPhoneSerializer(SignatureSerializer):
    username = serializers.CharField(max_length=128)
    phone = serializers.CharField(min_length=11, max_length=11)
