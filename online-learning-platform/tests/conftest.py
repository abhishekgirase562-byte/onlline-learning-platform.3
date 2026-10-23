import pytest
import os
import sys

# Ensure root directory is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app import create_app
from backend.config import init_db
from backend.seed import seed_database

@pytest.fixture(scope="session")
def app():
    # Force mock DB for completely isolated test execution
    test_config = {
        "TESTING": True,
        "FORCE_MOCK_DB": True,
        "SECRET_KEY": "test-secret-key-12345"
    }
    app = create_app(test_config=test_config)
    return app

@pytest.fixture(autouse=True)
def reset_db(app):
    with app.app_context():
        # Re-seed for fresh state before each test
        seed_database(quiet=True)

@pytest.fixture
def client(app):
    return app.test_client()
