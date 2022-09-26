import pytest
from api import app
from api.auth import oauth_scheme
from api.db import get_session
from test import test_client
from sqlmodel import Session

from .conftest import engine, fake_admin, fake_new_user, fake_user


new_email = "newnew@email.com"


@pytest.fixture(name="session", scope="session")
def session_fixture():
    with Session(engine) as session:
        yield session


def test_get_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    # existing user
    response = test_client.get(url=f"/user/?email={fake_user.email}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] is not None
    assert data["email"] == fake_user.email
    # non-existing user
    response = test_client.get(url="/user/?email=i@dont.exist")
    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_get_all_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    response = test_client.get(url="/users/")
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data[0] == {"email": fake_user.email, "id": 1}
    assert data[1] == {"email": fake_admin.email, "id": 2}


def test_create_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session

    # create new user requires authentication
    response = test_client.post("/user/", json=fake_new_user.dict())
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"

    # mock authentication
    app.dependency_overrides[oauth_scheme] = lambda: "mock_token"
    # create a new user
    response = test_client.post("/user/", json=fake_new_user.dict())
    data = response.json()
    assert response.status_code == 201
    assert data == {"email": fake_new_user.email, "id": 3}

    # attemp to create an already existing user
    response = test_client.post("/user/", json=fake_new_user.dict())
    data = response.json()
    assert response.status_code == 409
    assert data == {"detail": f"User <{fake_new_user.email}> already exists!"}

    app.dependency_overrides.clear()


def test_update_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    #  requires authentication
    response = test_client.put("/user/", json={"email": fake_user.email})
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"

    # mock authentication
    app.dependency_overrides[oauth_scheme] = lambda: "mock_token"

    # update to a new email
    response = test_client.put(f"/user/?email={fake_user.email}&new_email={new_email}")
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == new_email

    # update conflict -> attempt to change to an email already exists
    response = test_client.put(f"/user/?email={new_email}&new_email={fake_admin.email}")
    data = response.json()
    assert response.status_code == 409
    assert data["detail"] == f"<{fake_admin.email}> already exists"

    # attempt to update a non-existing user
    response = test_client.put("/user/?email=random@mail.com")
    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_delete_user(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    #  requires authentication
    response = test_client.delete("/user/", json={"email": new_email})
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Not authenticated"

    # mock authentication
    app.dependency_overrides[oauth_scheme] = lambda: "mock_token"

    # delete the 'new_email' user created by previous tests
    # maybe not a good idea and should be isoloated from other tests
    # refractor later
    response = test_client.delete(f"/user/?email={new_email}")
    assert response.status_code == 204

    # attempt to delete a non-existing user
    response = test_client.delete(f"/user/?email={new_email}")
    assert response.status_code == 404

    app.dependency_overrides.clear()
