from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    GROUP = 'group'
    PERSONAL = 'personal'

    CHAT_TYPE_CHOICES = [
        (GROUP, 'Group'),
        (PERSONAL, 'Personal'),
    ]

    name = models.CharField(max_length=50, null=True)
    type = models.CharField(
        max_length=10,
        choices=CHAT_TYPE_CHOICES,
        default=PERSONAL
    )
    members = models.ManyToManyField(
        User,
        through="ChatMembership",
        related_name="chatroom"
    )
    messages = models.ManyToManyField("Message", related_name="chatroom")

    def __str__(self):
        return self.name


class ChatMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey("ChatRoom", on_delete=models.CASCADE)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey("ChatRoom", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
