import os
import time
import hmac
import hashlib
import requests
import json

APP_KEY = os.environ["TTS_APP_KEY"]
APP_SECRET = os.environ["TTS_APP_SECRET"]
ACCESS_TOKEN = os.environ["TTS_ACCESS_TOKEN"]
CATEGORY_ASSET_CIPHER = os.environ["TEST_CIPHER"]
CAMPAIGN_ID = os.environ["TEST_CAMPAIGN_ID"]

BASE_URL = "https://open-api.tiktokglobalshop.com"
PATH = f"/affiliate_partner/202405/campaigns/{CAMPAIGN_ID}/products"


def sign_tts(path, params):
    filtered = {k: str(v) for k, v in params.items() if k not in ("sign", "access_token")}
    sign_str = APP_SECRET + path
    for k in sorted(filtered.keys()):
        sign_str += k + filtered[k]
    sign_str += APP_SECRET

    return hmac.new(
        APP_SECRET.encode(),
        sign_str.encode(),
        hashlib.sha256
    ).hexdigest()


def main():
    timestamp = str(int(time.time()))

    params = {
        "app_key": APP_KEY,
        "timestamp": timestamp,
        "category_asset_cipher": CATEGORY_ASSET_CIPHER,
        "page": 1,
        "page_size": 5,
    }

    params["sign"] = sign_tts(PATH, params)

    headers = {
        "x-tts-access-token": ACCESS_TOKEN,
        "content-type": "application/json"
    }

    url = BASE_URL + PATH
    resp = requests.get(url, params=params, headers=headers)

    print("HTTP:", resp.status_code)
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    main()
