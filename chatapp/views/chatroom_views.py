from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import ChatRoom, ChatMembership
from ..serializers import ChatRoomDetailSerializer, ChatRoomSerializer
from django.contrib.auth.models import User


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chatrooms_list(request):
    if request.method == 'POST':
        return create_chatroom(request)
    elif request.method == 'GET':
        return list_chatrooms(request)


def create_chatroom(request):
    data = JSONParser().parse(request)
    member_ids = data.pop('member_ids', [])
    member_ids.append(request.user.id)

    serializer = ChatRoomSerializer(data=data)
    if serializer.is_valid():

        chatroom = serializer.save()

        members = User.objects.filter(id__in=member_ids)
        if len(members) != len(member_ids):
            return Response({'error': 'One or more member_ids are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        for user in members:
            ChatMembership.objects.create(user=user, chatroom=chatroom)

        chatroom.refresh_from_db()
        response_serializer = ChatRoomDetailSerializer(chatroom)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def list_chatrooms(request):
    chatrooms = ChatRoom.objects.all()
    serializer = ChatRoomSerializer(chatrooms, many=True)
    return Response(serializer.data, safe=False, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def chatroom_detail(request, chatroom_id):
    if request.method == 'GET':
        return get_chatroom(request, chatroom_id)
    elif request.method == 'PUT':
        return update_chatroom(request, chatroom_id)
    elif request.method == 'DELETE':
        return delete_chatroom(request, chatroom_id)


def update_chatroom(request, chatroom_id):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'ChatRoom not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user not in chatroom.members.all():
        return Response({'error': 'You are not a member of this chatroom'}, status=status.HTTP_403_FORBIDDEN)

    data = JSONParser().parse(request)
    member_ids = data.pop('member_ids', [])

    serializer = ChatRoomSerializer(chatroom, data=data)
    if serializer.is_valid():

        chatroom = serializer.save()

        # Validate member_ids
        new_members = User.objects.filter(id__in=member_ids)
        if len(new_members) != len(member_ids):
            return Response({'error': 'One or more member_ids are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        current_members = set(chatroom.members.all())
        new_members_set = set(new_members)

        # Add new members
        for user in new_members_set - current_members:
            ChatMembership.objects.create(user=user, chatroom=chatroom)

        # Remove old members
        for user in current_members - new_members_set:
            ChatMembership.objects.filter(
                user=user, chatroom=chatroom).delete()

        chatroom.refresh_from_db()
        response_serializer = ChatRoomDetailSerializer(chatroom)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_chatroom(request, chatroom_id):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'ChatRoom not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ChatRoomDetailSerializer(chatroom)
    return Response(serializer.data, status=status.HTTP_200_OK)


def delete_chatroom(request, chatroom_id):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'ChatRoom not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user not in chatroom.members.all():
        return Response({'error': 'You are not a member of this chatroom'}, status=status.HTTP_403_FORBIDDEN)

    chatroom.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
