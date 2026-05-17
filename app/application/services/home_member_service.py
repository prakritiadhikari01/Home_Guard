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

    @transaction.atomic
    @staticmethod
    def add_member(
        acting_user,
        home,
        target_user,
        role=Role.MEMBER.value,
    ):

        acting_membership = (
            HomeMemberService.home_member_repository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can add members"
            )

        existing_member = (
            HomeMemberService.home_member_repository.member_exists(
                home=home,
                user=target_user,
            )
        )

        if existing_member:
            raise ValidationError(
                "User already exists in home"
            )

        permissions = (
            HomeMemberService.get_role_permissions(role)
        )

        return HomeMemberService.home_member_repository.create_member(
            home=home,
            user=target_user,
            role=role,
            **permissions
        )

    @transaction.atomic
    @staticmethod
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

    @transaction.atomic
    @staticmethod
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
    def get_role_permissions(role):
        permissions = (
            HomeMemberService.ROLE_PERMISSIONS.get(role)
        )

        if not permissions:
            raise ValidationError(
                "Invalid role permissions"
            )

        return permissions