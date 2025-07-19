import hashlib

from ManboAPIGateway.private_settings import UPAPI_KEY


def signature(params, apikey=UPAPI_KEY):
    sig = [f"{k}={v}" for k, v in params.items()]
    sig.sort()
    sig = "&".join(sig) + str(params["timestamp"]) + apikey
    sig = hashlib.sha256(sig.encode()).hexdigest()
    return sig
