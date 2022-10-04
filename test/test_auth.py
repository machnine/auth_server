from test import mock_settings, test_client
from unittest import mock

import pytest
from api import auth, crud
from api.exceptions import InvalidCredentialException
from api.model import Token, UserIn
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlmodel import Session

from .conftest import fake_admin, fake_user

new_email = "newnew@email.com"


def jwt_decoder(jwt_token: str, secret: str = mock_settings.access_token_secret):
    return jwt.decode(jwt_token, secret, algorithms=["HS256"])


def jwt_creator(
    email: str, secret: str = mock_settings.access_token_secret, minutes: int = 15
):
    return auth.create_jwt_token(email, secret, minutes)


def test_authenticate_user(db_session: Session):
    # failed non-existing
    failed_user = auth.authenticate_user(
        UserIn(email="any@email.com", password="anypass"), db_session
    )
    assert not failed_user

    # failed wrong password
    failed_user = auth.authenticate_user(
        UserIn(email=fake_user.email, password="anypass"), db_session
    )
    assert not failed_user

    # successful
    success_user = auth.authenticate_user(fake_user, db_session)
    assert success_user is not None
    assert success_user.email == fake_user.email


def test_create_jwt_token():
    secret = mock_settings.access_token_secret
    # token with default 15 mins expiry time
    token_15 = auth.create_jwt_token(new_email, secret)
    assert token_15 is not None
    decoded_15 = jwt_decoder(token_15)
    assert decoded_15["sub"] == new_email

    # not decodable by wrong secret
    with pytest.raises(JWTError):
        jwt_decoder(token_15, "WRONG_SECRET")

    # token with set expiry time
    token_99 = auth.create_jwt_token(new_email, secret, 99)
    assert token_99 is not None
    decoded_99 = jwt_decoder(token_99)
    assert decoded_99["sub"] == new_email

    # not decodable by wrong secret
    with pytest.raises(JWTError):
        jwt_decoder(token_99, "WRONG_SECRET")

    # expired token
    token_exp = auth.create_jwt_token(new_email, secret, -5)
    assert token_exp is not None
    with pytest.raises(ExpiredSignatureError):
        jwt_decoder(token_exp)


@mock.patch("api.auth.settings", mock_settings)
def test_create_access_token():
    access_token = jwt_creator(new_email)
    assert access_token is not None
    decoded_token = jwt_decoder(access_token)
    assert decoded_token["sub"] == new_email


@mock.patch("api.auth.settings", mock_settings)
def test_create_refresh_token():
    refresh_token = jwt_creator(new_email)
    assert refresh_token is not None
    decoded_token = jwt_decoder(refresh_token)
    assert decoded_token["sub"] == new_email


@mock.patch("api.auth.settings", mock_settings)
def test_get_user_from_refresh_token(db_session: Session):
    # refresh token without email encoded
    noemail_token = jwt_creator(email=None)
    with pytest.raises(InvalidCredentialException):
        auth.get_user_from_refresh_token(noemail_token, db_session)

    # refresh token with non-existing user
    nonuser_token = auth.create_refresh_token(email="random@email.com")
    with pytest.raises(InvalidCredentialException):
        auth.get_user_from_refresh_token(nonuser_token, db_session)

    # a real user
    user_token = auth.create_refresh_token(email=fake_user.email)
    # no stored refresh_token (logged out)
    with pytest.raises(InvalidCredentialException):
        auth.get_user_from_refresh_token(user_token, db_session)

    # logged in user has refresh_token
    crud.update_user(fake_user.email, db_session, refresh_token=user_token)
    # get user
    user = auth.get_user_from_refresh_token(user_token, db_session)
    assert user == fake_user.email


@mock.patch("api.auth.settings", mock_settings)
def test_post_admin_token():
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


@mock.patch("api.auth.settings", mock_settings)
def test_post_token():
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


@mock.patch("api.auth.settings", mock_settings)
def test_post_refresh(db_session: Session):
    # generate a refresh token and stored in mock db
    test_client.post("/token/", json=fake_user.dict())

    # read the refresh token
    user = crud.get_user(fake_user.email, db_session)
    # test the following endpoint wiht user.refresh_token
    response = test_client.post("/refresh/", json={"refresh_token": user.refresh_token})
    assert response.status_code == 200
    new_access_token = Token(**response.json())
    assert new_access_token.token_type == "bearer"
    assert new_access_token.access_token is not None

    # attempt to use a "valid" refresh token but not the one saved in the db
    # because the running time of this code is "too short" when using the same timedelta
    # use a different timedelta to generate a token differs from the stored one
    with mock.patch("api.auth.settings.refresh_token_expiry", 10):
        valid_refresh_token = auth.create_refresh_token(fake_user.email)
    response = test_client.post(
        "/refresh/", json={"refresh_token": valid_refresh_token}
    )
    assert response.status_code == 401
