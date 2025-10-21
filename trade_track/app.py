from flask import request, jsonify
from flask import Flask
import logging
from tasks import process_trade
from dotenv import load_dotenv
from log_config import setup_logging

setup_logging()

app = Flask(__name__)

load_dotenv()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.get_json(force=True)
        body = {}

        if isinstance(payload, list) and payload and 'body' in payload[0]:
            body = payload[0]['body']
        elif isinstance(payload, dict) and 'body' in payload:
            body = payload['body']
        elif isinstance(payload, dict) and 'data' in payload:
            body = payload
        else:
            return jsonify({"error": "Invalid payload format"}), 400

        raw_data = body.get('data', '')
        if not raw_data:
            return jsonify({"error": "Missing 'data' field"}), 400

        parsed = {}
        for line in raw_data.splitlines():
            if ':' in line:
                key, value = line.strip().split(':', 1)
                parsed[key.strip().lstrip('=')] = value.strip()

        required = ['Pair', 'Entry Price', 'Stop-Loss', 'Target/Exit Price']
        for field in required:
            if field not in parsed:
                return jsonify({"error": f"Missing field: {field}"}), 400

        logging.info(f"Parsed webhook data: {parsed}")

        # Delay task execution for 5 minutes
        process_trade.apply_async((parsed,), countdown=300)

        return jsonify({'status': 'queued', 'parsed_data': parsed}), 200

    except Exception as e:
        logging.exception("Webhook error")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000)

