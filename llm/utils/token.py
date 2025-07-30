import requests
import os
from datetime import datetime, timedelta

_token_cache = {"token": None, "expires_at": None}

def get_access_token():
    if _token_cache["token"] and _token_cache["expires_at"] > datetime.now():
        return _token_cache["token"]

    response = requests.post("http://tecerp.ampecportal.com/api/auth/login", data={
        "email": "frahman@totalelectrical.com.au",
        "password": "12345678"
    })

    data = response.json()
    token = data["access_token"]
    _token_cache["token"] = token
    _token_cache["expires_at"] = datetime.now() + timedelta(seconds=data.get("expires_in", 3600))

    return token
