import pytest
from trade_track.app import app
from trade_track.tasks import celery

@pytest.fixture
def client():
    app.testing = True
    # Run Celery tasks synchronously in tests
    celery.conf.update(task_always_eager=True)

    with app.test_client() as client:
        yield client