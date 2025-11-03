import pytest
from unittest.mock import patch
from trade_track.app import app
from trade_track.tasks import process_trade, celery

@pytest.fixture
def client():
    app.testing = True
    # Run Celery tasks synchronously in tests
    celery.conf.update(task_always_eager=True)

    with app.test_client() as client:
        yield client

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
