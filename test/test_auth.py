from test import test_client
from unittest import mock

from api import app
from api.auth import (
    authenticate_user,
    create_access_token,
    create_jwt_token,
    create_refresh_token,
    get_user_from_refresh_token,
)
from api.crud import get_user
from api.db import get_session
from api.model import Token, UserIn
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlmodel import Session

from .conftest import fake_admin, fake_user

new_email = "newnew@email.com"


# mock jwt secret
MOCK_JWT_SECRET = "TEMP_SECRET"


def jwt_decoder(jwt_token: str, secret: str = MOCK_JWT_SECRET):
    return jwt.decode(jwt_token, secret, algorithms=["HS256"])


def test_authenticate_user(db_session: Session):
    # failed non-existing
    failed_user = authenticate_user(
        UserIn(email="any@email.com", password="anypass"), db_session
    )
    assert not failed_user

    # failed wrong password
    failed_user = authenticate_user(
        UserIn(email=fake_user.email, password="anypass"), db_session
    )
    assert not failed_user

    # successful
    success_user = authenticate_user(fake_user, db_session)
    assert success_user is not None
    assert success_user.email == fake_user.email


def test_create_jwt_token():
    # token with default 15 mins expiry time
    token_15 = create_jwt_token(new_email, MOCK_JWT_SECRET)
    assert token_15 is not None
    decoded_15 = jwt_decoder(token_15)
    assert decoded_15["sub"] == new_email

    # not decodable by wrong secret
    try:
        wrong_15 = jwt_decoder(token_15, "WRONG_SECRET")
    except JWTError:
        wrong_15 = None
    assert wrong_15 is None

    # token with set expiry time
    token_99 = create_jwt_token(new_email, MOCK_JWT_SECRET, 99)
    assert token_99 is not None
    decoded_99 = jwt_decoder(token_99)
    assert decoded_99["sub"] == new_email

    # not decodable by wrong secret
    try:
        decoded_w99 = jwt_decoder(token_99, "WRONG_SECRET")
    except JWTError:
        decoded_w99 = None
    assert decoded_w99 is None

    # expired token
    token_exp = create_jwt_token(new_email, MOCK_JWT_SECRET, -5)
    assert token_exp is not None
    try:
        jwt_decoder(token_exp)
    except ExpiredSignatureError:
        assert True


def test_create_access_token():
    with mock.patch("api.config.settings.access_token_secret", MOCK_JWT_SECRET):
        access_token = create_access_token(email=new_email)
    assert access_token is not None
    decoded_token = jwt_decoder(access_token)
    assert decoded_token["sub"] == new_email


def test_create_refresh_token():
    with mock.patch("api.config.settings.refresh_token_secret", MOCK_JWT_SECRET):
        refresh_token = create_refresh_token(email=new_email)
    assert refresh_token is not None
    decoded_token = jwt_decoder(refresh_token)
    assert decoded_token["sub"] == new_email


def test_get_user_from_refresh_token(db_session: Session):
    with mock.patch("api.config.settings.refresh_token_secret", MOCK_JWT_SECRET):
        # refresh token without email encoded
        token_noemail = create_refresh_token(email=None)
        try:
            user_noemail = get_user_from_refresh_token(token_noemail, db_session)
        except Exception:
            user_noemail = None
        assert user_noemail is None

        # refresh token with non-existing user
        token_nonuser = create_refresh_token(email="random@email.com")
        try:
            non_user = get_user_from_refresh_token(token_nonuser, db_session)
        except Exception:
            non_user = None
        assert non_user is None


def test_post_admin_token(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    with mock.patch("api.config.settings.refresh_token_secret", MOCK_JWT_SECRET):
        with mock.patch("api.config.settings.access_token_secret", MOCK_JWT_SECRET):
            # login as an admin user
            response = test_client.post(
                "/admin_token/",
                data={"username": fake_admin.email, "password": fake_admin.password},
            )
            assert response.status_code == 200
            new_access_token = Token(**response.json())
            assert new_access_token.token_type == "bearer"
            assert new_access_token.access_token is not None

            # attempt to login as a non-admin user
            response = test_client.post(
                "/admin_token/",
                data={"username": fake_user.email, "password": fake_user.password},
            )
            assert response.status_code == 403

            # attempt to login with a non-existing user
            response = test_client.post(
                "/admin_token/",
                data={"username": "random@email.com", "password": "pass"},
            )
            assert response.status_code == 401
    app.dependency_overrides.clear()


def test_post_token(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    with mock.patch("api.config.settings.refresh_token_secret", MOCK_JWT_SECRET):
        with mock.patch("api.config.settings.access_token_secret", MOCK_JWT_SECRET):
            # generate token for existing user
            response = test_client.post("/token/", json=fake_user.dict())
            assert response.status_code == 200
            new_token = Token(**response.json())
            assert new_token.token_type == "bearer"
            assert new_token.access_token is not None
            assert new_token.refresh_token is not None

            # attempt to generate token for non-existing user
            response = test_client.post(
                "/token/", json={"email": "i@dont.exist", "password": "anything"}
            )
            assert response.status_code == 401

    app.dependency_overrides.clear()


def test_post_refresh(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    with mock.patch("api.config.settings.refresh_token_secret", MOCK_JWT_SECRET):
        with mock.patch("api.config.settings.access_token_secret", MOCK_JWT_SECRET):
            # generate a refresh token and stored in mock db
            test_client.post("/token/", json=fake_user.dict())

            # read the refresh token
            user = get_user(fake_user.email, db_session)
            # test the following endpoint wiht user.refresh_token
            response = test_client.post(
                "/refresh/", json={"refresh_token": user.refresh_token}
            )
            assert response.status_code == 200
            new_access_token = Token(**response.json())
            assert new_access_token.token_type == "bearer"
            assert new_access_token.access_token is not None

            # attempt to use a "valid" refresh token but not the one saved in the db

            # because the running time of this code is "too short" when using the same timedelta
            # use a different timedelta to generate a token differs from the stored one
            with mock.patch("api.config.settings.refresh_token_expiry", 10):
                valid_refresh_token = create_refresh_token(fake_user.email)
            print(user.refresh_token)
            print(valid_refresh_token)
            response = test_client.post(
                "/refresh/", json={"refresh_token": valid_refresh_token}
            )
            assert response.status_code == 401
    app.dependency_overrides.clear()
