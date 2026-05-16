from django.db import IntegrityError
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data

        try:
            user = User.objects.create_user(
                email=data.get("email"),
                full_name=data.get("full_name"),
                password=data.get("password"),
                phone=data.get("phone", None),
            )
        except IntegrityError:
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        print("HEADERS:", request.META.get("HTTP_AUTHORIZATION"))

        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    