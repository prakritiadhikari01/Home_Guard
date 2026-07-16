# app/interfaces/api/views/home_member_view.py
from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from app.application.services.home_invitation_service import HomeInvitationService
from app.domain.repositories import home_member_repository
from app.infrastructure.db.models.home_model import Home
from app.application.services.home_member_service import HomeMemberService

from app.interfaces.api.serializers.home_member_serializer import (
    AddHomeMemberSerializer,
    HomeMemberListSerializer,
    UpdateMemberRoleSerializer,
)


from django.core.mail import send_mail
from django.conf import settings
from app.infrastructure.db.repositories.django_home_member_repository import (
    DjangoHomeMemberRepository,
)

home_member_repository = DjangoHomeMemberRepository()
User = get_user_model()

class AddHomeMemberView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):

        serializer = AddHomeMemberSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        home = get_object_or_404(
            Home,
            id=home_id
        )

        permissions = HomeMemberService.get_role_permissions(
            serializer.validated_data["role"]
        )
        print("VIEW PERMISSIONS:", permissions)
        invitation = HomeInvitationService.send_invitation(
            acting_user=request.user,
            home=home,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
            permissions=permissions,
        )

        send_mail(
            subject="HomeGuard Invitation",
            message=(
                f"You have been invited to join '{home.name}'.\n\n"
                f"Login to HomeGuard and accept the invitation."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "Invitation sent successfully.",
                "email": invitation.email,
                "status": invitation.status,
            },
            status=status.HTTP_201_CREATED,
        )

class ListHomeMembersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, home_id):

        home = get_object_or_404(Home, id=home_id)

        member_repo = DjangoHomeMemberRepository()

        membership = member_repo.get_membership(
            home=home,
            user=request.user,
        )

        if not membership:
            raise PermissionDenied(
                "Access denied"
        )
        members = member_repo.get_home_members(home)

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
        print(serializer.validated_data)

        role = serializer.validated_data["role"]
        overrides = {
            k: v for k in ("can_control_devices", "can_manage_members", "can_unlock_door", "receive_alerts")
            if (v := serializer.validated_data.get(k)) is not None
        }

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
                permission_overrides=overrides or None,
            )
        )

        return Response({
            "message": "Role updated",
            "role": member.role,
            "can_control_devices": member.can_control_devices,
            "can_manage_members": member.can_manage_members,
            "can_unlock_door": member.can_unlock_door,
            "receive_alerts": member.receive_alerts,
        })
    
class MyHomeMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id):
        home = get_object_or_404(Home, id=home_id)
        membership = home_member_repository.get_membership(home, request.user)

        if membership is None:
            return Response({"detail": "Not a member of this home."}, status=403)

        return Response({
            "role": membership.role,
            "permissions": {
                "can_control_devices": membership.can_control_devices,
                "can_manage_members": membership.can_manage_members,
                "can_unlock_door": membership.can_unlock_door,
                "receive_alerts": membership.receive_alerts,
            },
        })
    
