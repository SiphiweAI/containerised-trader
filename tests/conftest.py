import pytest
from trade_track.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

