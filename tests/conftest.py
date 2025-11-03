import pytest
from unittest.mock import patch
from trade_track.app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

@patch("trade_track.tasks.load_trade_data", return_value=None)
def test_webhook(mock_load, client):
    response = client.post("/webhook", json={"body": {"data": "Pair: EUR/USD\nEntry Price: 1.1\nStop-Loss: 1.0\nTarget/Exit Price: 1.2"}})
    assert response.status_code == 200
