import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/")
def root():
    return "OK - tts-pull-data is running", 200

@app.get("/run")
def run_job():
    # Example: call like /run?campaign_id=xxx&cipher=yyy
    campaign_id = request.args.get("campaign_id", "")
    cipher = request.args.get("cipher", "")
    return jsonify({
        "ok": True,
        "message": "Endpoint works. Next: call TikTok + write to BigQuery here.",
        "campaign_id": campaign_id,
        "cipher": cipher,
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
