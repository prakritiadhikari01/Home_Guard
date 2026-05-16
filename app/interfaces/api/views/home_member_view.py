from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.infrastructure.db.models.home_model import Home
from app.application.services.home_member_service import HomeMemberService

from app.interfaces.api.serializers.home_member_serializer import (
    AddHomeMemberSerializer,
    HomeMemberListSerializer,
    UpdateMemberRoleSerializer,
)
from app.infrastructure.db.repositories.home_member_repo import (
    HomeMemberRepository,
)
User = get_user_model()


class AddHomeMemberView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):

        serializer = AddHomeMemberSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        home = get_object_or_404(Home, id=home_id)

        target_user = get_object_or_404(
            User,
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


class ListHomeMembersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, home_id):

        home = get_object_or_404(Home, id=home_id)

        membership = (
            HomeMemberRepository.get_membership(
                home=home,
                user=request.user,
            )
        )
        if not membership:
            raise PermissionDenied(
                "Access denied"
        )
        members = (
            HomeMemberRepository.get_home_members(home)
        )

        serializer = HomeMemberListSerializer(
            members,
            many=True,
        )

        return Response(serializer.data)
    
class RemoveHomeMemberView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, home_id, user_id):

        home = get_object_or_404(Home, id=home_id)

        target_user = get_object_or_404(
            User,
            id=user_id
        )

        HomeMemberService.remove_member(
            acting_user=request.user,
            home=home,
            target_user=target_user,
        )

        return Response({
            "message": "Member removed successfully"
        })
    
class UpdateMemberRoleView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, home_id, user_id):
        
        serializer = UpdateMemberRoleSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data["role"]

        home = get_object_or_404(Home, id=home_id)

        target_user = get_object_or_404(
            User,
                id=user_id
        )

        member = (
            HomeMemberService.update_member_role(
                acting_user=request.user,
                home=home,
                target_user=target_user,
                role=role,
            )
        )

        return Response({
            "message": "Role updated",
            "role": member.role,
        })