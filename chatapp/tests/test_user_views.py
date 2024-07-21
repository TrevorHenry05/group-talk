import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_not_authenticated(api_client):
    url = reverse('user-list')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('register')
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'password' not in response.data
    assert User.objects.count() == 1
    assert User.objects.get().username == 'testuser'


@pytest.mark.django_db
def test_user_registration_username_exists(api_client):
    url = reverse('register')
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    api_client.post(url, data, format='json')

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_login(api_client):
    url = reverse('register')
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    api_client.post(url, data, format='json')

    url = reverse('login')
    data = {
        "username": data["username"],
        "password": data["password"],
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'refresh' in response.data
    assert 'access' in response.data
    assert 'password' not in response.data


@pytest.mark.django_db
def test_user_login_invalid_credentials(api_client):
    url = reverse('register')
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    api_client.post(url, data, format='json')

    url = reverse('login')
    data = {
        "username": data["username"],
        "password": "wrongpassword",
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_users(auth_client):
    api_client, user = auth_client
    url = reverse('user-list')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['username'] == user.username


@pytest.mark.django_db
def test_retrieve_user(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email
    assert 'password' not in response.data
    assert 'chatrooms' in response.data


@pytest.mark.django_db
def test_retrieve_user_not_found(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id + 1])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_user(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id])
    data = {
        "username": "newusername",
        "email": user.email,
    }

    response = api_client.put(url, data, format='json')

    user.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert user.username == data['username']
    assert user.email == data['email']
    assert user.check_password('testpassword')


@pytest.mark.django_db
def test_update_user_not_found(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id + 1])
    data = {
        "username": "newusername",
        "email": user.email,
    }

    response = api_client.put(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_user(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_delete_user_not_found(auth_client):
    api_client, user = auth_client
    url = reverse('user-detail', args=[user.id + 1])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert User.objects.count() == 1
