import os, time, hmac, hashlib, json
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
        if s == "":
            continue
        filtered[k] = s

    sign_string = secret + path
    for k in sorted(filtered.keys()):
        sign_string += k + filtered[k]
    sign_string += (body_str or "") + secret

    return hmac.new(secret.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).hexdigest()

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
        return {"http": r.status_code, "url": r.url, "json": {"raw": r.text[:500]}}

    return {"http": r.status_code, "url": r.url, "json": j}


@app.get("/")
def root():
    return "OK - tts-pull-data is running", 200

@app.get("/health")
def health():
    return jsonify(ok=True), 200

@app.get("/category-assets")
def category_assets():
    # NOTE: endpoint version/path must be correct for your product.
    # If this returns 404 Invalid path, it means the endpoint is wrong in TikTok docs for your account.
    resp = tts_get("/affiliate_partner/202405/category_assets", {"version": "202405"})
    return jsonify(resp), resp["http"]

# Example placeholder route (we’ll wire properly after auth works)
@app.get("/pull-campaigns")
def pull_campaigns():
    cipher = request.args.get("cipher", "").strip()
    page = request.args.get("page", "1")
    page_size = request.args.get("page_size", "50")
    if not cipher:
        return jsonify(ok=False, error="Missing cipher"), 400

    path = "/affiliate_partner/202405/campaigns"
    query = {
        "version": "202405",
        "category_asset_cipher": cipher,
        "page": page,
        "page_size": page_size,
        "type": request.args.get("type", "MY_CAMPAIGNS"),
        "query_type_filter": "DEFAULT",
    }
    resp = tts_get(path, query)
    return jsonify(resp), resp["http"]
