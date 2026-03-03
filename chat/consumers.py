import json
import profile
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, RoomMember, Message
from django.utils import timezone
from channels.db import database_sync_to_async
from accounts.models import Profile


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_uuid = self.scope['url_route']['kwargs']['room_uuid']
        self.room_group_name = f'chat_{self.room_uuid}'

        # print("WebSocket connect triggered")
        # print("User:", self.user)
        # print("Room UUID:", self.room_uuid)

        # reject anonymous user
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        # checking if room exists
        try:
            self.room = await ChatRoom.objects.aget(uuid=self.room_uuid)
        except ChatRoom.DoesNotExist:
            await self.close()
            return

        # checking if user is a member of the room
        is_member = await RoomMember.objects.filter(
            room=self.room,
            user=self.user
        ).aexists()

        if not is_member:
            await self.close()
            return

        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            "presence_global",
            self.channel_name
        )

        await self.accept()

        # mark user as online
        await self.update_user_online_status(True)

        # broadcast to room group that user is online
        await self.channel_layer.group_send(
            "presence_global",
            {
                "type": "user_status",
                "user_id": self.user.id,
                "username": self.user.username,
                "is_online": True,
            }
        )

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # mark user as offline
        await self.update_user_online_status(False)

        # broadcast to room group that user is offline
        await self.channel_layer.group_send(
            "presence_global",
            {
                "type": "user_status",
                "user_id": self.user.id,
                "username": self.user.username,
                "is_online": False,
            }
        )

    async def receive(self, text_data):
        """Triggered when client sends message through websocket"""

        data = json.loads(text_data)
        content = data.get("content")

        if not content:
            return

        # save message to database
        message = await Message.objects.acreate(
            room=self.room,
            sender=self.user,
            content=content,
            message_type="text"

        )

        # broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message_id": message.id,
                "content": message.content,
                "sender": self.user.username,
                "created_at": str(message.created_at)
            }
        )

    async def chat_message(self, event):
        """Triggered when a message is sent to the room group"""

        await self.send(text_data=json.dumps({
            "message_id": event["message_id"],
            "content": event["content"],
            "sender": event["sender"],
            "created_at": event["created_at"]
        }))

    async def user_status(self, event):
        """Triggered when a user comes online or goes offline"""

        await self.send(text_data=json.dumps({
            "type": "presence",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_online": event["is_online"]
        }))

    @database_sync_to_async
    def update_user_online_status(self, is_online):
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.is_online = is_online
        profile.last_seen = timezone.now()
        profile.save()
