from unittest.mock import patch
from trade_track.tasks import process_trade

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'

def test_webhook(client):
    trade_data = {
        "body": {
            "data": (
                "Pair: EUR/USD\n"
                "Entry Price: 1.1\n"
                "Stop-Loss: 1.0\n"
                "Target/Exit Price: 1.2\n"
                "Verdict: Win"
            )
        }
    }

    # Patch apply_async to prevent real Celery call
    with patch.object(process_trade, "apply_async") as mock_task:
        response = client.post("/webhook", json=trade_data)
        assert response.status_code == 200
        mock_task.assert_called_once()
