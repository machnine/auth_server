import pytest
from api.crud import create_user, update_user
from api.model import UserCreate
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# mock data
fake_user = UserCreate(email="fake_user@email.com", password="fakepassword")
fake_admin = UserCreate(email="fake_admin@email.com", password="fakeadminpass")
fake_new_user = UserCreate(email="fake_new@example.com", password="fakenewuserpass")


engine = create_engine(
    url="sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)

# database session fixture
# named as db_session to distinguish from test session
@pytest.fixture(name="db_session", scope="session")
def session_fixture():
    with Session(engine) as session:
        yield session


def pytest_sessionstart(session):
    """
    Called after the test Session object has been created and
    before performing collection and entering the run test loop.
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        create_user(fake_user, db)
        create_user(fake_admin, db)
        update_user(fake_admin.email, db, is_admin=1)
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
