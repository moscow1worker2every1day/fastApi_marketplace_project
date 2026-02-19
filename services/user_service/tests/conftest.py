import pytest
from tests.unit.fake_users import UserFactory


@pytest.fixture(scope="session")
def fake_user():
    return UserFactory()
