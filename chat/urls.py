from django.urls import path
from .views import PrivateChatView

urlpatterns = [
    path('private/', PrivateChatView.as_view(), name='private-chat')
]