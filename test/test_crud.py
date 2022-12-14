"""
Testing for api/crud.py: The orders of the test_ functions are important!
So temporarily created data can be properly removed (by the tests) before
starting the next testing file
"""

import pytest
from sqlmodel import Session
from api import crud
from sqlalchemy.exc import IntegrityError
from api.config import settings

from .conftest import FakeUser


def test_crud_get_single_user(db_session: Session):
    # get single user from db
    user = crud.get_user(FakeUser.user.email, db_session)
    assert user.id is not None
    assert user.email == FakeUser.user.email
    # non-existing user
    user_notexist = crud.get_user("i@dont.exist", db_session)
    assert user_notexist is None


def test_crud_get_all_users(db_session: Session):
    users = crud.get_all_users(db_session)
    assert users is not None
    assert users[0].email == FakeUser.user.email
    assert users[1].email == FakeUser.admin.email


def test_crud_create_user(db_session: Session):
    # create new user
    user_created = crud.create_user(FakeUser.new, db_session)
    assert user_created.email == FakeUser.new.email

    # attempt to create an exisiting users
    with pytest.raises(IntegrityError):
        crud.create_user(FakeUser.new, db_session)


def test_update_user(db_session: Session):
    # attempt to update non-existing user

    user_notexist = crud.update_user("i@dont.exist", db_session)
    assert user_notexist is None

    # attempt to update causing conflict in email duplication
    # inject a user first
    new_user = crud.create_user(FakeUser.new, db_session)
    assert new_user.email == FakeUser.new.email
    # check excetion is raised
    with pytest.raises(IntegrityError):
        crud.update_user(
            FakeUser.new.email,
            db_session,
            new_email=FakeUser.admin.email,
        )

    # update existing user
    user_exist = crud.update_user(
        FakeUser.new.email,
        db_session,
        is_admin=1,
    )
    assert user_exist.email == FakeUser.new.email
    assert user_exist.is_admin == 1

    # update existing user password
    user_newpass = crud.update_user(
        FakeUser.new.email,
        db_session,
        password="1234",
    )
    assert user_newpass is not None
    assert settings.pwd_context.verify("1234", user_newpass.hashed_password)


def test_crud_delete_user(db_session: Session):
    # delete user and get_user to check
    crud.delete_user(FakeUser.new.email, db_session)
    user_deleted = crud.get_user(FakeUser.new.email, db_session)

    assert user_deleted is None
