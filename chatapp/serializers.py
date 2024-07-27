from rest_framework import serializers
from .models import ChatRoom, ChatMembership, Message
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        extra_kwargs = {
            'id': {'read_only': True},
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                return user
            raise serializers.ValidationError("Incorrect Credentials")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'chatroom', 'content', 'timestamp']
        extra_kwargs = {
            'id': {'read_only': True},
            'timestamp': {'read_only': True},
        }


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    members = UserListSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'type', 'members', 'messages']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserListSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'type', 'members']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class UserDetailSerializer(serializers.ModelSerializer):
    chatrooms = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "chatrooms"]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_chatrooms(self, obj):
        chatrooms = ChatRoom.objects.filter(members=obj)
        return ChatRoomSerializer(chatrooms, many=True).data


class ChatMembershipSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    chatroom = serializers.PrimaryKeyRelatedField(
        queryset=ChatRoom.objects.all()
    )

    class Meta:
        model = ChatMembership
        fields = ['id', 'user', 'chatroom']
        extra_kwargs = {
            'id': {'read_only': True},
        }
