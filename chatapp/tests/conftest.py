import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import ChatRoom


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        user = User.objects.create_user(**kwargs)
        return user
    return make_user


@pytest.fixture
def get_token(create_user):
    def generate_token(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    return generate_token


@pytest.fixture
def auth_client(api_client, create_user, get_token):
    user = create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )
    tokens = get_token(user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
    return api_client, user
