import requests
import os
import json

AUTH_FILE = "llm/token.json"

LARAVEL_URL = "https://tecerp.ampecportal.com"

LOGIN_PAYLOAD = {
    "email": "frahman@totalelectrical.com.au",
    "password": "12345678"
}

def save_token(token):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump({"token": token}, f)


def load_token():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f).get("token")
    return None


def get_new_token():
    try:
        response = requests.post(
            f"{LARAVEL_URL}/api/auth/login",
            data=LOGIN_PAYLOAD  # Use 'data=', not 'json='
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if token:
            save_token(token)
        return token
    except Exception as e:
        print("Auth failed:", e)
        return None


def get_auth_token():
    token = load_token()
    if not token:
        token = get_new_token()
    return token


def call_laravel_api(endpoint, data=None, method="GET"):
    token = get_auth_token()
    if not token:
        return {"error": "Authentication failed"}

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{LARAVEL_URL}/api/{endpoint}"

    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, params=data, headers=headers)

        if response.status_code == 401:
            # Token expired → try refresh once
            token = get_new_token()
            if not token:
                return {"error": "Re-authentication failed"}
            headers["Authorization"] = f"Bearer {token}"
            if method == "POST":
                response = requests.post(url, json=data, headers=headers)
            else:
                response = requests.get(url, params=data, headers=headers)

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON from Laravel"}

