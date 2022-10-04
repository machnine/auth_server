import pytest
from api import crud
from api.model import UserCreate
from sqlmodel import SQLModel
from test import override_get_session, test_engine

# mock data
fake_user = UserCreate(email="fake_user@email.com", password="fakepassword")
fake_admin = UserCreate(email="fake_admin@email.com", password="fakeadminpass")
fake_new_user = UserCreate(email="fake_new@example.com", password="fakenewuserpass")


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
        crud.create_user(fake_user, db)
        crud.create_user(fake_admin, db)
        crud.update_user(fake_admin.email, db, is_admin=1)
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
