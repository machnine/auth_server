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


def pytest_sessionstart(session):
    """
    Called after the test Session object has been created and
    before performing collection and entering the run test loop.
    """
    SQLModel.metadata.create_all(test_engine)

    with next(override_get_session()) as db:
        crud.create_user(FakeUser.user, db)
        crud.create_user(FakeUser.admin, db)
        crud.update_user(FakeUser.admin.email, db, is_admin=1)
        db.commit()


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    SQLModel.metadata.clear()


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    pass


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
    pass
