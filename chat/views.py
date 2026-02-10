from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import ChatRoom, RoomMember
from .serializers import PrivateChatCreateSerializer, GroupChatCreateSerializer

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
