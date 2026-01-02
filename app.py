cat > app.py <<'PY'
import os
import time
import hmac
import hashlib
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

BASE_URL = os.getenv("TTS_BASE_URL", "https://open-api.tiktokglobalshop.com")

def must_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def clean_params(d: dict) -> dict:
    out = {}
    for k, v in (d or {}).items():
        if v is None:
            continue
        s = str(v).strip()
        if s == "":
            continue
        out[k] = s
    return out

def sign_tts(path: str, params: dict, body_str: str = "") -> str:
    """
    TikTok Shop signature:
      sign_string = app_secret + path + (sorted key+value, excluding sign & access_token) + body + app_secret
      sign = HMAC-SHA256(sign_string, app_secret).hexdigest()
    """
    app_secret = must_env("TTS_APP_SECRET")

    filtered = {}
    for k, v in params.items():
        if k in ("sign", "access_token"):
            continue
        if v is None:
            continue
        s = str(v).strip()
        if s == "":
            continue
        filtered[k] = s

    sign_string = app_secret + path
    for k in sorted(filtered.keys()):
        sign_string += k + filtered[k]
    sign_string += (body_str or "") + app_secret

    return hmac.new(app_secret.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).hexdigest()

def tts_get(path: str, query: dict) -> dict:
    app_key = must_env("TTS_APP_KEY")
    access_token = must_env("TTS_ACCESS_TOKEN")
    timestamp = str(int(time.time()))

    q = clean_params({**query, "app_key": app_key, "timestamp": timestamp})
    q["sign"] = sign_tts(path, q, body_str="")

    url = f"{BASE_URL}{path}"
    r = requests.get(
        url,
        params=q,
        headers={
            "x-tts-access-token": access_token,
            "content-type": "application/json",
        },
        timeout=60,
    )

    try:
        data = r.json()
    except Exception:
        return {"http": r.status_code, "url": r.url, "json": {"code": -1, "message": "Non-JSON", "raw": r.text[:500]}}

    return {"http": r.status_code, "url": r.url, "json": data}

@app.get("/")
def home():
    return "OK - tts-pull-data is running", 200

@app.get("/health")
def health():
    return jsonify(ok=True), 200

@app.get("/category-assets")
def category_assets():
    # NOTE: endpoint path may differ by API version for your account.
    # This is just a placeholder route that proves routing works.
    # You can later swap to the correct TikTok endpoint after auth is fixed.
    return jsonify(ok=True, message="Route works. Now fix TikTok auth/sign then call real API."), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
PY
