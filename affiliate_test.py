cat > affiliate_test.py << 'EOF'
import os, time, hmac, hashlib, requests, json

BASE="https://open-api.tiktokglobalshop.com"
PATH="/affiliate_partner/202405/campaigns"
APP_KEY=os.environ["TTS_APP_KEY"].strip()
APP_SECRET=os.environ["TTS_APP_SECRET"].strip()
TOKEN=os.environ["TTS_ACCESS_TOKEN"].strip()
CIPHER=os.environ.get("CATEGORY_ASSET_CIPHER","").strip()

def sign(path, params, body=""):
    filtered={k:str(v) for k,v in params.items() if k not in ("sign","access_token") and str(v)!=""}
    s=APP_SECRET + path + "".join(k+filtered[k] for k in sorted(filtered)) + (body or "") + APP_SECRET
    return hmac.new(APP_SECRET.encode(), s.encode(), hashlib.sha256).hexdigest()

ts=str(int(time.time()))
params={
  "app_key": APP_KEY,
  "timestamp": ts,
  "version": "202405",
  "page": 1,
  "page_size": 1,
}
# only add cipher if you have it
if CIPHER:
  params["category_asset_cipher"]=CIPHER

params["sign"]=sign(PATH, params)

r=requests.get(BASE+PATH, params=params, headers={"x-tts-access-token":TOKEN, "content-type":"application/json"}, timeout=30)
print("URL:", r.url)
print("HTTP:", r.status_code)
try:
  print(json.dumps(r.json(), indent=2)[:2000])
except:
  print(r.text[:2000])
EOF
python3 affiliate_test.py
