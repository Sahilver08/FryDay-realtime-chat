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
