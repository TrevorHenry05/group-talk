from django.urls import path
from .views import user_views as UserViews
from .views import chatroom_views as ChatroomViews
from .views import message_views as MessageViews
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # User URLs
    path('register/', UserViews.register_user, name='register'),
    path('login/', UserViews.login_user, name='login'),
    path('users/', UserViews.user_detail, name='users'),
    path('users/all/', UserViews.list_users, name='list_users'),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),

    # Chatroom URLs
    path('chatrooms/', ChatroomViews.chatrooms_list, name='chatrooms_list'),
    path(
        'chatrooms/<int:chatroom_id>/',
        ChatroomViews.chatroom_detail,
        name='chatrooms_detail'
    ),

    # Message URLs
    path(
        'messages/chatrooms/<int:chatroom_id>/',
        MessageViews.create_message,
        name='create_message'
    ),
    path(
        'messages/<int:message_id>/',
        MessageViews.message_detail,
        name='message_detail'
    ),
]
