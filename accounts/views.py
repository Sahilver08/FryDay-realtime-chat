from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
 
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class TestAuthView(APIView):
    def get(self, request):
        return Response({
            "message": "You are authenticated",
            "user": request.user.username
        })