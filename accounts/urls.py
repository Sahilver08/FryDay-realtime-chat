from django.urls import path
from .views import RegisterView, TestAuthView

urlpatterns = [
    path('register/',RegisterView.as_view(), name='register'),
    path('test-auth/', TestAuthView.as_view(), name='test_auth'),
]