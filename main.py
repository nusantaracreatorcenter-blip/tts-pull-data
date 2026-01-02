import os, time, hmac, hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_URL = "https://open-api.tiktokglobalshop.com"

def must_env(k: str) -> str:
    v = os.getenv(k, "").strip()
    if not v:
        raise RuntimeError(f"Missing env var: {k}")
    return v

def sign_tts(path: str, params: dict, body_str: str = "") -> str:
    secret = must_env("TTS_APP_SECRET")
    filtered = {}
    for k, v in params.items():
        if k in ("sign", "access_token"):
            continue
        if v is None:
            continue
        s = str(v).strip()
        if s:
            filtered[k] = s

    sign_string = secret + path
    for k in sorted(filtered.keys()):
        sign_string += k + filtered[k]
    sign_string += (body_str or "") + secret

    return hmac.new(secret.encode(), sign_string.encode(), hashlib.sha256).hexdigest()

def tts_get(path: str, query: dict):
    app_key = must_env("TTS_APP_KEY")
    token = must_env("TTS_ACCESS_TOKEN")
    ts = str(int(time.time()))

    params = {**query, "app_key": app_key, "timestamp": ts}
    params["sign"] = sign_tts(path, params, "")

    url = BASE_URL + path
    r = requests.get(url, params=params, headers={"x-tts-access-token": token}, timeout=60)

    try:
        j = r.json()
    except Exception:
        j = {"raw": r.text[:500]}
    return r.status_code, r.url, j

@app.get("/")
def root():
    return "OK - tts-pull-data is running", 200

@app.get("/health")
def health():
    return jsonify(ok=True), 200

@app.get("/category-assets")
def category_assets():
    status, url, j = tts_get("/affiliate_partner/202405/category_assets", {"version": "202405"})
    return jsonify(http=status, url=url, json=j), status
