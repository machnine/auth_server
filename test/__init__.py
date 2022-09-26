from fastapi.testclient import TestClient

from api import app

test_client = TestClient(app)
