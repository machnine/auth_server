from test import test_client


def test_root():
    response = test_client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
