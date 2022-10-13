from dataclasses import dataclass
from test import test_engine

import pytest
from api import crud
from api.model import UserCreate
from sqlmodel import Session, SQLModel


# mock data
@dataclass
class FakeUser:
    user = UserCreate(email="fake_user@email.com", password="fakepassword")
    admin = UserCreate(email="fake_admin@email.com", password="fakeadminpass")
    new = UserCreate(email="fake_new@example.com", password="fakenewuserpass")


# database session fixture
@pytest.fixture()
def db_session():
    # create all tables
    SQLModel.metadata.create_all(test_engine)
    # inject a couple of test users
    with Session(test_engine) as session:
        crud.create_user(FakeUser.user, session)
        crud.create_user(FakeUser.admin, session)
        crud.update_user(FakeUser.admin.email, session, is_admin=1)
        session.commit()

        yield session

    # clean up database
    # close session
    session.close()
    # delete all tables
    SQLModel.metadata.drop_all(test_engine)
