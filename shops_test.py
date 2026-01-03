cat > shops_test.py << 'EOF'
import os
import time
import hmac
import hashlib
import requests
import json

APP_KEY = os.environ["TTS_APP_KEY"]
APP_SECRET = os.environ["TTS_APP_SECRET"]
ACCESS_TOKEN = os.environ["TTS_ACCESS_TOKEN"]

BASE_URL = "https://open-api.tiktokglobalshop.com"
PATH = "/authorization/202309/shops"

def sign_tts(path, params):
    params = {k: str(v) for k, v in params.items() if k not in ("sign", "access_token")}
    sign_string = path
    for k in sorted(params.keys()):
        sign_string += k + params[k]
    sign_string = APP_SECRET + sign_string + APP_SECRET
    return hmac.new(
        APP_SECRET.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).hexdigest()

ts = str(int(time.time()))
params = {
    "app_key": APP_KEY,
    "timestamp": ts
}
params["sign"] = sign_tts(PATH, params)

url = BASE_URL + PATH
headers = {
    "x-tts-access-token": ACCESS_TOKEN,
    "content-type": "application/json"
}

r = requests.get(url, params=params, headers=headers, timeout=30)

print("HTTP:", r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
EOF
