from unittest import mock

from api.db import get_session

from .conftest import engine


def test_get_session():
    # check if the mocking using in memory engine is successful
    with mock.patch("api.db.engine", engine):
        with next(get_session()) as session:
            assert session.connection().engine.url == engine.url
