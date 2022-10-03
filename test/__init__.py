from api import app
from api.config import Settings
from fastapi.testclient import TestClient

test_client = TestClient(app)

# mock API settings
mock_settings = Settings(
    access_token_secret="aCcEsS_sEcRet", refresh_token_secret="ReFrEsH_sEcRet"
)
