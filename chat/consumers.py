import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, RoomMember, Message


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

        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
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
