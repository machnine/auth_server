from test import test_client


def test_root():
    """
    Check if the app is working and root is not routed to anything
    """
    response = test_client.get("/")
    assert response.status_code == 404
