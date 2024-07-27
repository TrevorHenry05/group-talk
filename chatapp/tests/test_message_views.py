import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from ..models import ChatRoom, Message


@pytest.mark.django_db
def test_create_message(auth_client):
    # Setup
    api_client, user = auth_client
    url = reverse('chatrooms_list')
    data = {
        "name": "Test Chatroom",
        "type": ChatRoom.GROUP,
        "member_ids": []
    }

    response = api_client.post(url, data, format='json')
    chatroom = ChatRoom.objects.get()

    url = reverse('create_message', args=[chatroom.id])
    data = {
        "content": "Test message",
    }

    # Action
    response = api_client.post(url, data, format='json')
    message = response.data

    # Validation
    assert response.status_code == status.HTTP_201_CREATED
    assert Message.objects.count() == 1
    assert message['content'] == data['content']
    assert message['timestamp'] is not None
    assert message['user'] == user.id
    assert message['chatroom'] == chatroom.id


@pytest.mark.django_db
def test_create_message_chatroom_does_not_exist(auth_client):
    # Setup
    api_client, _ = auth_client
    url = reverse('create_message', args=[1])
    data = {
        "content": "Test message"
    }

    # Action
    response = api_client.post(url, data, format='json')

    # Validation
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_message_user_not_member(auth_client):
    # Setup
    api_client, _ = auth_client
    chatroom = ChatRoom.objects.create(
        name="Test Chatroom",
        type=ChatRoom.GROUP
    )

    url = reverse('create_message', args=[chatroom.id])
    data = {
        "content": "Test message"
    }

    # Action
    response = api_client.post(url, data, format='json')

    # Validation
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'You are not a member of this chatroom' in response.data['error']


@pytest.mark.django_db
def test_update_message(auth_client):
    # Setup
    api_client, user = auth_client
    chatroom = ChatRoom.objects.create(
        name="Test Chatroom",
        type=ChatRoom.GROUP
    )
    chatroom.members.add(user)

    message = Message.objects.create(
        user=user,
        chatroom=chatroom,
        content="Test message"
    )

    url = reverse('message_detail', args=[message.id])
    data = {
        "content": "Updated message"
    }

    # Action
    response = api_client.put(url, data, format='json')
    message.refresh_from_db()

    # Validation
    assert response.status_code == status.HTTP_200_OK
    assert message.content == data['content']


@pytest.mark.django_db
def test_update_message_message_does_not_exist(auth_client):
    # Setup
    api_client, _ = auth_client
    url = reverse('message_detail', args=[1])
    data = {
        "content": "Updated message"
    }

    # Action
    response = api_client.put(url, data, format='json')

    # Validation
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_message_user_not_author(auth_client):
    # Setup
    api_client, _ = auth_client
    user = User.objects.create(
        username="user2",
        email="testemail@test.com",
        password="testpassword"
    )

    chatroom = ChatRoom.objects.create(
        name="Test Chatroom",
        type=ChatRoom.GROUP
    )
    chatroom.members.add(user)

    message = Message.objects.create(
        user=user,
        chatroom=chatroom,
        content="Test message"
    )

    url = reverse('message_detail', args=[message.id])

    data = {
        "content": "Updated message"
    }

    # Action
    response = api_client.put(url, data, format='json')

    # Validation
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'You are not the author of this message' in response.data['error']


@pytest.mark.django_db
def test_delete_message(auth_client):
    # Setup
    api_client, user = auth_client
    chatroom = ChatRoom.objects.create(
        name="Test Chatroom",
        type=ChatRoom.GROUP
    )
    chatroom.members.add(user)

    message = Message.objects.create(
        user=user,
        chatroom=chatroom,
        content="Test message"
    )

    url = reverse('message_detail', args=[message.id])

    # Action
    response = api_client.delete(url)

    # Validation
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Message.objects.count() == 0
