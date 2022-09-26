from api.model import UserCreate
from sqlmodel.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from api.crud import create_user, update_user

# mock data
fake_user = UserCreate(email="fake_user@email.com", password="fakepassword")
fake_admin = UserCreate(email="fake_admin@email.com", password="fakeadminpass")
fake_new_user = UserCreate(email="fake_new@example.com", password="fakenewuserpass")


engine = create_engine(
    url="sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        create_user(fake_user, session)
        create_user(fake_admin, session)
        update_user(fake_admin.email, session, is_admin=1)
        session.commit()


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
