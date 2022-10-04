from test import test_client

from api import app
from api.auth import oauth_scheme
from api.db import get_session
from sqlmodel import Session

from .conftest import FakeUser

new_email = "newnew@email.com"


def test_get_user(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    # existing user
    response = test_client.get(url=f"/user/?email={FakeUser.user.email}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] is not None
    assert data["email"] == FakeUser.user.email
    # non-existing user
    response = test_client.get(url="/user/?email=i@dont.exist")
    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_get_all_user(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    response = test_client.get(url="/users/")
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data[0] == {"email": FakeUser.user.email, "id": 1}
    assert data[1] == {"email": FakeUser.admin.email, "id": 2}


def test_create_user(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session

    # create new user requires authentication
    response = test_client.post("/user/", json=FakeUser.new.dict())
    data = response.json()

    assert response.status_code == 401

    # mock authentication
    app.dependency_overrides[oauth_scheme] = lambda: "mock_token"
    # create a new user
    response = test_client.post("/user/", json=FakeUser.new.dict())
    data = response.json()
    assert response.status_code == 201
    assert data == {"email": FakeUser.new.email, "id": 3}

    # attemp to create an already existing user
    response = test_client.post("/user/", json=FakeUser.new.dict())
    data = response.json()
    assert response.status_code == 409
    assert data == {"detail": f"User <{FakeUser.new.email}> already exists!"}

    app.dependency_overrides.clear()


def test_update_user(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    #  requires authentication
    response = test_client.put("/user/", json={"email": FakeUser.user.email})
    data = response.json()
    assert response.status_code == 401

    # mock authentication
    app.dependency_overrides[oauth_scheme] = lambda: "mock_token"

    # update to a new email
    response = test_client.put(f"/user/?email={FakeUser.user.email}&new_email={new_email}")
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == new_email

    # update conflict -> attempt to change to an email already exists
    response = test_client.put(f"/user/?email={new_email}&new_email={FakeUser.admin.email}")
    data = response.json()
    assert response.status_code == 409
    assert data["detail"] == f"<{FakeUser.admin.email}> already exists"

    # attempt to update a non-existing user
    response = test_client.put("/user/?email=random@mail.com")
    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_delete_user(db_session: Session):
    app.dependency_overrides[get_session] = lambda: db_session
    #  requires authentication
    response = test_client.delete("/user/", json={"email": new_email})
    assert response.status_code == 401

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
