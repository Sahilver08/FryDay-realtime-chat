from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import ChatRoom, RoomMember, Message
from .serializers import PrivateChatCreateSerializer, GroupChatCreateSerializer, ChatRoomListSerializer, MessageSerializer
from django.core.paginator import Paginator

# Create your views here.


class PrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PrivateChatCreateSerializer(
            data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        other_user_id = serializer.validated_data['user_id']

        # Checking if private room already exists
        existing_room = (
            ChatRoom.objects
            .filter(room_type='private')
            .filter(members__user=request.user)
            .filter(members__user_id=other_user_id)
            .distinct()
            .first()
        )

        if existing_room:
            return Response({
                "room_id": existing_room.uuid,
                "message": "Private chat already exists"
            })

        # Create new private room
        room = ChatRoom.objects.create(
            room_type='private', created_by=request.user)

        RoomMember.objects.create(room=room, user=request.user)
        RoomMember.objects.create(room=room, user_id=other_user_id)

        return Response({
            'room_id': room.uuid,
            'message': 'Private chat created successfully'})


class GroupChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GroupChatCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        user_ids = serializer.validated_data['user_ids']

        # create group room
        room = ChatRoom.objects.create(
            room_type='group', name=name, created_by=request.user
        )

        # creator is admin
        RoomMember.objects.create(
            room=room, user=request.user, role='admin'
        )

        # add other members
        RoomMember.objects.bulk_create([
            RoomMember(room=room, user_id=user_id)
            for user_id in user_ids
        ])

        return Response({
            "room_id": room.uuid,
            "name": room.name,
            "message": "Group chat created"
        })


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = (
            ChatRoom.objects
            .filter(members__user=request.user)
            .distinct()
            .order_by('-created_at')
        )

        serializer = ChatRoomListSerializer(
            rooms,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # print("REQUEST DATA:", request.data)
        room_id = request.data.get('room')

        if not room_id:
            return Response(
                {"error": "Room ID is required."}, status=400
            )

        try:
            room = ChatRoom.objects.get(uuid=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Room not Found"}, status=404

            )

        #Ensure user is member
        if not RoomMember.objects.filter(room=room, user=request.user).exists():
            return Response(
                {"error": "You are not a member of this room."}, status=403
            )

        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save(
            sender=request.user,
            room=room
        )

        return Response(
            MessageSerializer(message).data,
            status=201
        )


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        room_id = request.query_params.get('room')
        page_number = request.query_params.get('page', 1)

        if not room_id:
            return Response(
                {"error": "Room ID is required."}, status=400
            )

        try:
            room = ChatRoom.objects.get(uuid=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Room Not Found"}, status=404
            )

        if not RoomMember.objects.filter(
            room=room,
            user=request.user
        ).exists():
            return Response(
                {"error": "You are not a member of this room."}, status=403
            )

        messages = (
            Message.objects.filter(room=room).order_by('-created_at')
        )

        paginator = Paginator(messages, 20)
        page = paginator.get_page(page_number)

        serializer = MessageSerializer(page, many=True)

        return Response({
            "messages": serializer.data,
            "has_next": page.has_next()
        })