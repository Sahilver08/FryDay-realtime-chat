from django.urls import path
from .views import PrivateChatView, GroupChatView, ChatListView, SendMessageView, MessageListView

urlpatterns = [
    path('private/', PrivateChatView.as_view(), name='private-chat'),
    path('group/', GroupChatView.as_view(), name='group-chat'),
    path('list/', ChatListView.as_view(), name='chat-list'),
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('messages/', MessageListView.as_view(), name='message-list'),
]
