from rest_framework.exceptions import Throttled
from rest_framework.throttling import ScopedRateThrottle


class CustomThrottled(Throttled):
    def __init__(self, detail):
        self.detail = detail


class CustomScopedThrottle(ScopedRateThrottle):
    def throttle_failure(self):
        raise CustomThrottled(detail={
            "code": 5,
            "success": False,
            "message": "请求速率过快",
            "result": None
        })
