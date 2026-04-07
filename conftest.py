"""Root conftest for pytest-django."""

import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow DB access in all tests by default."""
    pass
