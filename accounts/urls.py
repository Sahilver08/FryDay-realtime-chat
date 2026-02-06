from django.urls import path
from .views import RegisterView, TestAuthView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('test-auth/', TestAuthView.as_view(), name='test_auth'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
