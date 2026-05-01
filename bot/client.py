import os
import time
import hmac
import hashlib
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


# Custom Exceptions

class APIError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"APIError {code}: {msg}")


class NetworkError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"NetworkError: {reason}")


# Load credentials

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "keys.env"))

API_KEY    = os.getenv("BINANCE_API_KEY", "").strip()
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "").strip()
BASE_URL   = os.getenv("BASE_URL", "https://testnet.binancefuture.com").strip()

if not API_KEY or not SECRET_KEY:
    raise EnvironmentError("API_KEY or SECRET_KEY missing. Check keys.env path and contents.")


# Signature helper

def _sign(params: dict) -> str:
    query_string = urlencode(params)
    return hmac.new(
        key=SECRET_KEY.encode("utf-8"),
        msg=query_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


# Core request sender

def send_order(params: dict) -> dict:
    url = f"{BASE_URL}/fapi/v1/order"

    params["timestamp"] = int(time.time() * 1000)  # 1. timestamp first
    params["signature"] = _sign(params)             # 2. sign after timestamp

    headers = {"X-MBX-APIKEY": API_KEY}

    try:
        response = requests.post(url, params=params, headers=headers, timeout=10)
    except requests.ConnectionError as exc:
        raise NetworkError(f"Connection failed: {exc}") from exc
    except requests.Timeout as exc:
        raise NetworkError(f"Request timed out: {exc}") from exc

    data = response.json()

    # HTTP level error
    if response.status_code != 200:
        raise APIError(
            code=response.status_code,
            msg=data.get("msg", response.text),
        )

    # Binance error payload (negative codes only)
    if "code" in data and int(data["code"]) < 0:
        raise APIError(code=data["code"], msg=data.get("msg", "Unknown API error"))

    return data


if __name__ == "__main__":
    import json

    test_params = {
        "symbol":      "BTCUSDT",
        "side":        "BUY",
        "type":        "LIMIT",
        "timeInForce": "GTC",
        "quantity":    0.01,
        "price":       50000,
    }

    try:
        result = send_order(test_params)
        print(json.dumps(result, indent=2))
    except (APIError, NetworkError) as err:
        print(err)