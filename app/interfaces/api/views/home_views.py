#app/interfaces/api/views/home_views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.home_service import HomeService
from app.interfaces.api.permissions.face_permissions import IsFaceEnrolled
from app.interfaces.api.serializers.home_serializer import (
    HomeCreateSerializer,
    HomeListSerializer,
)
from rest_framework.exceptions import PermissionDenied
from app.interfaces.api.serializers.home_serializer import SecurityModeUpdateSerializer
from django.shortcuts import get_object_or_404
from app.infrastructure.db.models.home_model import Home
class HomeCreateView(APIView):

    permission_classes = [IsAuthenticated,IsFaceEnrolled]

    def post(self, request):

        serializer = HomeCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        result = HomeService.create_home(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        data = HomeCreateSerializer(result["home"]).data
        return Response(data, status=status.HTTP_201_CREATED)


class UserHomesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        homes = HomeService.get_user_homes(request.user)

        serializer = HomeListSerializer(homes, many=True)

        return Response(serializer.data)



class UpdateSecurityModeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, home_id):
        home = get_object_or_404(Home, id=home_id)
        if home.owner_id != request.user.id:
            raise PermissionDenied("Only the home owner can change the security mode.")

        serializer = SecurityModeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        home.security_mode = serializer.validated_data["security_mode"]
        home.save(update_fields=["security_mode"])
        return Response({"security_mode": home.security_mode})