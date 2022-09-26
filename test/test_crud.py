"""
Testing for api/crud.py: The orders of the test_ functions are important!
So temporarily created data can be properly removed (by the tests) before
starting the next testing file
"""

import pytest
from sqlmodel import Session
from api.crud import create_user, update_user, get_user, get_all_users, delete_user
from api.db import get_session
from api import app
from sqlalchemy.exc import IntegrityError
from api.config import settings

from .conftest import engine, fake_new_user, fake_user, fake_admin


@pytest.fixture(name="session", scope="session")
def session_fixture():
    with Session(engine) as session:
        yield session


def test_crud_get_single_user(session: Session):
    # get single user from db
    app.dependency_overrides[get_session] = lambda: session
    user = get_user(fake_user.email, session)
    assert user.id is not None
    assert user.email == fake_user.email
    # non-existing user
    user_notexist = get_user("i@dont.exist", session)
    assert user_notexist is None
    app.dependency_overrides.clear()


def test_crud_get_all_users(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    users = get_all_users(session)
    assert users is not None
    assert users[0].email == fake_user.email
    assert users[1].email == fake_admin.email
    app.dependency_overrides.clear()


def test_crud_create_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session

    # create new user
    user_created = create_user(fake_new_user, session)
    assert user_created.email == fake_new_user.email

    # attempt to create an exisiting users
    try:
        user_conflict = create_user(fake_new_user, session)
    except IntegrityError:
        user_conflict = None
    assert user_conflict is None
    app.dependency_overrides.clear()


def test_update_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    # attempt to update non-existing user

    user_notexist = update_user("i@dont.exist", session)
    assert user_notexist is None
    # attempt to update causing conflict in email duplication
    try:
        user_conflict = update_user(
            fake_new_user.email, session, new_email=fake_admin.email
        )
    except IntegrityError:
        user_conflict = None
    assert user_conflict is None

    # update existing user
    user_exist = update_user(fake_new_user.email, session, is_admin=1)
    assert user_exist.email == fake_new_user.email
    assert user_exist.is_admin == 1

    # update existing user password
    user_newpass = update_user(fake_new_user.email, session, password="1234")
    assert user_newpass is not None
    assert settings.pwd_context.verify("1234", user_newpass.hashed_password)

    app.dependency_overrides.clear()


def test_crud_delete_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    # delete user and get_user to check
    delete_user(fake_new_user.email, session)
    user_deleted = get_user(fake_new_user.email, session)

    assert user_deleted is None

    app.dependency_overrides.clear()
