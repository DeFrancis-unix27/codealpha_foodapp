from django.shortcuts import render
from .models import *
from django.contrib.auth import authenticate
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
# Create your views here.


class register(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer


class Login(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "no such user found"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": f"welcome {user.username} to foodbank",
                "refresh": str(refresh),
                "access_token": str(refresh.access_token),
            }
        )

class CreateResturant(generics.CreateAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permissions_classess = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role !=  "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class UpdateResturant(generics.UpdateAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permissions_classess = [IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.role !=  "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)

class ListResturant(generics.ListAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permissions_classess = [AllowAny]

class RetriveResturant(generics.RetrieveAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permissions_classess = [IsAuthenticated]

    def perform_retrieve(self, serializer):
        if self.request.user.role !=  "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)