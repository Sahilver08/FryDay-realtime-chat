from django.contrib import admin
from .models import ChatRoom,RoomMember,Message,MessageStatus
# Register your models here.


admin.site.register(ChatRoom)
admin.site.register(RoomMember)
admin.site.register(Message)
admin.site.register(MessageStatus)