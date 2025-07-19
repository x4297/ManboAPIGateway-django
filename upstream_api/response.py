from rest_framework import status as _status
from rest_framework.response import Response as _Response


class Response(_Response):
    def __init__(self, code: int, status=_status.HTTP_200_OK, message=None, data=None):
        tmp = {
            "code": code,
            "success": True if code == 0 else False,
            "message": message,
            "result": {
                "total": len(data),
                "data": data
            } if data is not None else None
        }
        super().__init__(tmp, status)
