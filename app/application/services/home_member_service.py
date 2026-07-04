#app/application/services/home_member_service.py
from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import PermissionDenied
from django.db import transaction
from app.domain.value_objects.role import Role
from app.domain.services.access_policy import AccessPolicy

from app.infrastructure.db.repositories.django_home_member_repository import (
    DjangoHomeMemberRepository,
)
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
)
from app.infrastructure.db.models.home_invitation_model import (
    HomeInvitation,
)

class HomeMemberService:
    home_member_repository = (
        DjangoHomeMemberRepository()
    )
    ROLE_PERMISSIONS = {
        Role.OWNER.value: {
            "can_control_devices": True,
            "can_manage_members": True,
            "can_unlock_door": True,
            "receive_alerts": True,
        },

        Role.ADMIN.value: {
            "can_control_devices": True,
            "can_manage_members": True,
            "can_unlock_door": True,
            "receive_alerts": True,
        },

        Role.MEMBER.value: {
            "can_control_devices": False,
            "can_manage_members": False,
            "can_unlock_door": False,
            "receive_alerts": True,
        },

        Role.GUEST.value: {
            "can_control_devices": False,
            "can_manage_members": False,
            "can_unlock_door": False,
            "receive_alerts": False,
        },

        Role.SECURITY.value: {
            "can_control_devices": False,
            "can_manage_members": False,
            "can_unlock_door": True,
            "receive_alerts": True,
        },
    }

    @staticmethod
    @transaction.atomic
    def add_member(
        acting_user,
        home,
        email,
        role=Role.MEMBER.value,
    ):

        acting_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=acting_user,
            )
        )
        if acting_user.email == email:
            raise ValidationError(
                "You cannot invite yourself."
            )
        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can add members"
            )

        permissions = (
            HomeMemberService.get_role_permissions(role)
        )

        existing_pending = (
            HomeMemberService.home_member_repository
            .get_pending_invitation(home, email)
        )

        if existing_pending:
            raise ValidationError(
                "Invitation already pending."
            )
        existing_user = (
            HomeMemberService.home_member_repository
            .get_user_by_email(email)
        )

        if existing_user:
            existing_member = (
                HomeMemberService.home_member_repository
                .get_membership(
                    home=home,
                    user=existing_user,
                )
            )
            if existing_member:
                raise ValidationError(
                    "User is already a member of this home."
                )
        invitation = (
            HomeMemberService.home_member_repository.create_invitation(
                home=home,
                email=email,
                invited_by=acting_user,
                role=role,
                permissions=permissions,
            )
        )

        return invitation
    
    @staticmethod
    @transaction.atomic
    def remove_member(
        acting_user,
        home,
        target_user,
    ):

        acting_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can remove members"
            )
        if acting_user == target_user:
            raise ValidationError(
            "Owner cannot remove themselves"
            )

        target_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=target_user,
            )
        )

        if not target_membership:
            raise NotFound("Member not found")

        return HomeMemberService.home_member_repository.remove_member(
            home=home,
            user=target_user,
        )

    @staticmethod
    @transaction.atomic
    def update_member_role(
        acting_user,
        home,
        target_user,
        role,
    ):

        acting_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can update roles"
            )

        if role == Role.OWNER.value:
            if role not in [
                r.value for r in Role
            ]:
                raise ValidationError(
                    "Invalid role"
                )
            raise ValidationError(
                "Cannot assign OWNER role"
            )
        
        target_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=target_user,
            )
        )

        if not target_membership:
            raise NotFound("Member not found")
        if target_membership.role == Role.OWNER.value:
            raise ValidationError(
                "Owner role cannot be modified"
            )
        permissions = (
            HomeMemberService.get_role_permissions(role)
        )

        return HomeMemberService.home_member_repository.update_role(
            membership=target_membership,
            role=role,
            permissions=permissions,
        )

    @staticmethod
    @transaction.atomic
    def accept_invitation(invitation, user):

        invitation.status = "accepted"
        invitation.save()

        permissions = invitation.permissions

        membership = (
            HomeMemberService.home_member_repository.create_member(
                home=invitation.home,
                user=user,
                role=invitation.role,
                can_view_dashboard=True,
                can_control_devices=permissions["can_control_devices"],
                can_manage_members=permissions["can_manage_members"],
                can_unlock_door=permissions["can_unlock_door"],
                receive_alerts=permissions["receive_alerts"],
            )
        )
        HomeInvitation.objects.filter(
            home=invitation.home,
            email=user.email,
            status="pending",
        ).exclude(
            id=invitation.id,
        ).delete()
        return membership


    @staticmethod
    @transaction.atomic
    def reject_invitation(invitation):

        invitation.status = "rejected"
        invitation.save()

        return invitation

  
    @staticmethod
    def get_pending_invitations(user):

        from app.infrastructure.db.models.home_invitation_model import (
            HomeInvitation,
        )

        return HomeInvitation.objects.filter(
            email=user.email,
            status="pending",
        ).select_related(
            "home",
            "invited_by",
        )
    
    @staticmethod
    def get_role_permissions(role):
        permissions = (
            HomeMemberService.ROLE_PERMISSIONS.get(role)
        )

        if not permissions:
            raise ValidationError(
                "Invalid role permissions"
            )

        return permissions