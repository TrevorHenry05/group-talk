import pytest
from django.urls import reverse
from rest_framework import status
from ..models import ChatRoom, ChatMembership
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_create_chatroom(auth_client):
    # Setup
    api_client, user = auth_client
    url = reverse('chatrooms_list')
    data = {
        "name": "Test Chatroom",
        "type": ChatRoom.GROUP,
        "member_ids": []
    }

    # Action
    response = api_client.post(url, data, format='json')
    chatroom = ChatRoom.objects.get()

    # Validation
    assert response.status_code == status.HTTP_201_CREATED
    assert ChatRoom.objects.count() == 1
    assert chatroom.name == data['name']
    assert chatroom.type == ChatRoom.GROUP
    assert len(chatroom.members.all()) == 1
    assert ChatMembership.objects.count() == 1
    assert ChatMembership.objects.get().user == user


@pytest.mark.django_db
def test_update_chatroom(auth_client):
    # Setup
    api_client, user = auth_client
    chatroom = ChatRoom.objects.create(
        name="Test Chatroom",
        type=ChatRoom.GROUP
    )
    chatroom.members.add(user)

    user_2 = User.objects.create(
        username="user2",
        email="test2@eample.com",
        password="testpassword"
    )

    url = reverse('chatrooms_detail', args=[chatroom.id])
    data = {
        "name": "Updated Chatroom",
        "type": ChatRoom.GROUP,
        "member_ids": [user.id, user_2.id]
    }

    # Action
    response = api_client.put(url, data, format='json')
    chatroom.refresh_from_db()

    # Validation
    assert response.status_code == status.HTTP_200_OK
    assert chatroom.name == data['name']
    assert chatroom.type == ChatRoom.GROUP
    assert len(chatroom.members.all()) == 2
    assert ChatMembership.objects.count() == 2
