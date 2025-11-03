from flask import Flask, request, jsonify
import logging
import os
from trade_track.tasks import process_trade
from trade_track.log_config import setup_logging
from trade_track.helper_funcs import validate_env_vars
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

if "PYTEST_CURRENT_TEST" not in os.environ:
    validate_env_vars()

setup_logging()
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

# Load .env only in local development
if os.getenv("FLASK_ENV") == "development" and os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

@app.route("/webhook", methods=["POST"])
@limiter.limit("10 per minute")
def webhook():
    try:
        payload = request.get_json(force=True)
        body = {}

        if isinstance(payload, list) and payload and "body" in payload[0]:
            body = payload[0]["body"]
        elif isinstance(payload, dict) and "body" in payload:
            body = payload["body"]
        elif isinstance(payload, dict) and "data" in payload:
            body = payload
        else:
            return jsonify({"error": "Invalid payload format"}), 400

        raw_data = body.get("data", "")
        if not raw_data:
            return jsonify({"error": "Missing 'data' field"}), 400

        parsed = {}
        for line in raw_data.splitlines():
            if ":" in line:
                key, value = line.strip().split(":", 1)
                parsed[key.strip().lstrip("=")] = value.strip()

        required = ["Pair", "Entry Price", "Stop-Loss", "Target/Exit Price"]
        for field in required:
            if field not in parsed:
                return jsonify({"error": f"Missing field: {field}"}), 400

        logging.info(f"Parsed webhook data: {parsed}")

        process_trade.apply_async((parsed,), countdown=300)

        return jsonify({"status": "queued", "parsed_data": parsed}), 200

    except Exception as e:
        logging.exception("Webhook error")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
