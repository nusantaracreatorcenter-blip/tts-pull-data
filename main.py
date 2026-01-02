import os, time, json, hmac, hashlib
from flask import Flask, request, jsonify
import requests

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
    # secret + path + sorted(key+value) + body + secret, HMAC-SHA256
    secret = must_env("TTS_APP_SECRET")

    filtered = {}
    for k, v in params.items():
        if k in ("sign", "access_token"):
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

def tts_get(path: str, query: dict) -> dict:
    app_key = must_env("TTS_APP_KEY")
    access_token = must_env("TTS_ACCESS_TOKEN")
    ts = str(int(time.time()))

    q = clean_params({**query, "app_key": app_key, "timestamp": ts})
    q["sign"] = sign_tts(path, q, body_str="")

    url = f"{BASE_URL}{path}"
    r = requests.get(url, params=q, headers={"x-tts-access-token": access_token}, timeout=60)
    try:
        j = r.json()
    except Exception:
        j = {"non_json": r.text[:300]}
    return {"http": r.status_code, "url": r.url, "json": j}

@app.get("/health")
def health():
    return jsonify(ok=True)

@app.get("/debug-auth")
def debug_auth():
    # simple endpoint to test your creds against one API call
    campaign_id = request.args.get("campaign_id", "")
    cipher = request.args.get("cipher", "")
    if not campaign_id or not cipher:
        return jsonify(ok=False, need="campaign_id & cipher in querystring"), 400

    path = f"/affiliate_partner/202405/campaigns/{campaign_id}/products"
    resp = tts_get(path, {"category_asset_cipher": cipher, "PageNo": 1, "PageSize": 1, "version": "202405"})
    return jsonify(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
