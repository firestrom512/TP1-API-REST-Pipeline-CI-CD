"""Fixtures partagées : remise à zéro avant chaque test."""

import pytest

from src.app import app
from src.data import reset_data


@pytest.fixture
def client():
    reset_data()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
    reset_data()
