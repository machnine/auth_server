from api import app
from api.config import Settings
from api.db import get_session
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

# mock API settings
mock_settings = Settings(
    access_token_secret="aCcEsS_sEcRet",
    refresh_token_secret="ReFrEsH_sEcRet",
)

# test database engine
test_engine = create_engine(
    url="sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# override in app db connection dependancy
def override_get_session():
    try:
        session = Session(test_engine)
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_get_session


test_client = TestClient(app)
