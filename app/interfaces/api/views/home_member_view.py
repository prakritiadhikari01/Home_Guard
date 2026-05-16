from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth import get_user_model

from app.infrastructure.db.models.home_model import Home
from app.application.services.home_member_service import HomeMemberService

from app.interfaces.api.serializers.home_member_serializer import (
    AddHomeMemberSerializer,
)

User = get_user_model()


class AddHomeMemberView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):

        serializer = AddHomeMemberSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        home = Home.objects.get(id=home_id)

        target_user = User.objects.get(
            id=serializer.validated_data["user_id"]
        )

        member = HomeMemberService.add_member(
            acting_user=request.user,
            home=home,
            target_user=target_user,
            role=serializer.validated_data["role"],
        )

        return Response(
            {
                "message": "Member added successfully",
                "user": target_user.email,
                "role": member.role,
            },
            status=status.HTTP_201_CREATED,
        )