import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, RoomMember


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_uuid = self.scope['url_route']['kwargs']['room_uuid']
        self.room_group_name = f'chat_{self.room_uuid}'

        print("WebSocket connect triggered")
        print("User:", self.user)
        print("Room UUID:", self.room_uuid)

        # reject anonymous user
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        # checking if room exists
        try:
            room = await ChatRoom.objects.aget(uuid=self.room_uuid)
        except ChatRoom.DoesNotExist:
            await self.close()
            return

        # checking if user is a member of the room
        is_member = await RoomMember.objects.filter(
            room=room,
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
