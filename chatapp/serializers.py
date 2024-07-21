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

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
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


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class UserDetailedSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = ChatMembership
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }
