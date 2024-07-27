from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import ChatRoom, Message
from ..serializers import MessageSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_message(request, chatroom_id):
    data = JSONParser().parse(request)
    try:
        chatroom = ChatRoom.objects.get(id=chatroom_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chatroom does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.user not in chatroom.members.all():
        return Response({'error': f'You are not a member of this chatroom {chatroom.members.all()}'}, status=status.HTTP_400_BAD_REQUEST)

    message = {
        'user': request.user.id,
        'chatroom': chatroom.id,
        'content': data['content']
    }

    serializer = MessageSerializer(data=message)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def message_detail(request, message_id):
    if request.method == 'DELETE':
        return delete_message(request, message_id)
    elif request.method == 'PUT':
        return update_message(request, message_id)


def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': 'Message does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != message.user:
        return Response({'error': 'You are not the author of this message'}, status=status.HTTP_403_FORBIDDEN)

    message.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def update_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': 'Message does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != message.user:
        return Response({'error': 'You are not the author of this message'}, status=status.HTTP_403_FORBIDDEN)

    data = JSONParser().parse(request)
    message.content = data['content']
    message.save()

    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_200_OK)
