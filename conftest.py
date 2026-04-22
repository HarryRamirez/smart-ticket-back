import pytest
from ddf import G, N
from django.contrib.auth.models import User
from tests.factories import UserFactory, UserFactoryFaker 



@pytest.fixture
def user_creation():
    return UserFactoryFaker()