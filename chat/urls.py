from django.urls import path
from .views import PrivateChatView, GroupChatView

urlpatterns = [
    path('private/', PrivateChatView.as_view(), name='private-chat'),
    path('group/', GroupChatView.as_view(), name='group-chat'),
]
