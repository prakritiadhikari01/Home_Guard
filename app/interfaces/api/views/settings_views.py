from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.settings_service import SettingsService
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.repositories.django_home_member_repository import DjangoHomeMemberRepository
from app.interfaces.api.serializers.settings_serializer import (
    SettingsSerializer,
    HomeSettingsSerializer,
    UserSettingsSerializer,
)


class SettingsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        home_id = request.query_params.get("home_id")
        data = SettingsService.get_settings(request.user, home_id)
        serializer = SettingsSerializer(data)
        return Response(serializer.data)

    def patch(self, request):
        home_id = request.query_params.get("home_id")
        data = SettingsService.get_settings(request.user, home_id)

        if "home_settings" in request.data:
            home = get_object_or_404(Home, id=home_id)
            membership = DjangoHomeMemberRepository().get_membership(home=home, user=request.user)
            if not membership or not membership.can_manage_members:
                raise PermissionDenied("You don't have permission to edit home settings.")

            serializer = HomeSettingsSerializer(
                data["home_settings"], data=request.data["home_settings"], partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if "user_settings" in request.data:
            serializer = UserSettingsSerializer(
                data["user_settings"], data=request.data["user_settings"], partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({"message": "Settings updated successfully."})