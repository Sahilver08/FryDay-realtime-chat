import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ChatRoom(models.Model):

    ROOM_TYPE_CHOICES= (
        ("private", "Private"),
        ("group", "Group"),
    )

    id=models.BigAutoField(primary_key=True)

    uuid=models.UUIDField(
        default = uuid.uuid4,
        editable=False,
        unique=True
    )

    room_type=models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES
    )

    name=models.CharField(
        max_length=225,
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_rooms" 
    )

    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes=[
            models.Index(fields=["room_type"]),
        ]

    def __str__(self):
        return f"{self.room_type} - {self.uuid}"


class RoomMember(models.Model):
    ROLE_CHOICES= (
        ("admin","Admin"),
        ("member","Member"),
    )

    room= models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    is_muted = models.BooleanField(default=False)

    class Meta:
        unique_together=("room","user")
        indexes =[
            models.Index(fields=["room","user"])
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.room.id}"
    

class Message(models.Model):

    MESSAGE_TYPE_CHOICE=(
        ("text","Text"),
        ("image","Image"),
        ("file","File"),
    )

    id = models.BigAutoField(primary_key=True)

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    content = models.TextField(blank=True)

    file = models.FileField(
        upload_to="chat_files/",
        null= True,
        blank=True
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICE,
        default="text"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room","created_at"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
        

class MessageStatus(models.Model):

    STATUS_CHOICES=(
        ("sent","Sent"),
        ("delivered","Delivered"),
        ("seen","Seen"),
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="statuses",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_status"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="sent"
    )

    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message","user")
        indexes = [
            models.Index(fields=["message","user"]),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.status}"

