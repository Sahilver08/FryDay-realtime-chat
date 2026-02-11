from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatRoom, RoomMember


class PrivateChatCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        request = self.context['request']

        if request.user.id == value:
            raise serializers.ValidationError("You cannot chat with yourself")

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exists.")

        return value


class GroupChatCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate_user_ids(self, value):
        request = self.context['request']

        # remove duplicates
        unique_ids = set(value)

        # Creater should not be in the list of members
        unique_ids.discard(request.user.id)

        if len(unique_ids) < 1:
            raise serializers.ValidationError(
                "Group must have at least 2 members including creator."
            )

        existing_users = User.objects.filter(id__in=unique_ids).count()

        if existing_users != len(unique_ids):
            raise serializers.ValidationError(
                "One or more users do not exist.")

        return list(unique_ids)


class ChatRoomListSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['uuid', 'room_type', 'display_name', 'created_at']

    def get_display_name(self, obj):
        request = self.context['request']

        if obj.room_type == 'group':
            return obj.name

        # For private chat, display the other user's username
        other_member = obj.members.exclude(
            user=request.user
        ).select_related('user').first()

        return other_member.user.username if other_member else "Unknown"
        