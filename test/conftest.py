from dataclasses import dataclass
from test import override_get_session, test_engine

import pytest
from api import crud
from api.model import UserCreate
from sqlmodel import SQLModel


# mock data
@dataclass
class FakeUser:
    user = UserCreate(email="fake_user@email.com", password="fakepassword")
    admin = UserCreate(email="fake_admin@email.com", password="fakeadminpass")
    new = UserCreate(email="fake_new@example.com", password="fakenewuserpass")


# database session fixture
@pytest.fixture
def db_session():
    return next(override_get_session())


def inject_fake_users():
    with next(override_get_session()) as db:
        crud.create_user(FakeUser.user, db)
        crud.create_user(FakeUser.admin, db)
        crud.update_user(FakeUser.admin.email, db, is_admin=1)
        db.commit()


def pytest_sessionstart(session):
    SQLModel.metadata.create_all(test_engine)
    inject_fake_users()


def pytest_sessionfinish(session, exitstatus):
    SQLModel.metadata.drop_all(test_engine)
