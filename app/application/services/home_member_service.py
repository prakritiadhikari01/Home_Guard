from django.core.exceptions import PermissionDenied

from app.domain.value_objects.role import Role
from app.domain.services.access_policy import AccessPolicy

from app.infrastructure.db.repositories.home_member_repo import (
    HomeMemberRepository,
)


class HomeMemberService:

    @staticmethod
    def add_member(
        acting_user,
        home,
        target_user,
        role=Role.MEMBER.value,
    ):

        acting_membership = (
            HomeMemberRepository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can add members"
            )

        existing_member = (
            HomeMemberRepository.member_exists(
                home=home,
                user=target_user,
            )
        )

        if existing_member:
            raise Exception(
                "User already exists in home"
            )

        permissions = (
            HomeMemberService.get_role_permissions(role)
        )

        return HomeMemberRepository.create_member(
            home=home,
            user=target_user,
            role=role,
            **permissions
        )

    @staticmethod
    def remove_member(
        acting_user,
        home,
        target_user,
    ):

        acting_membership = (
            HomeMemberRepository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can remove members"
            )

        return HomeMemberRepository.remove_member(
            home=home,
            user=target_user,
        )

    @staticmethod
    def update_member_role(
        acting_user,
        home,
        target_user,
        role,
    ):

        acting_membership = (
            HomeMemberRepository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(acting_membership):
            raise PermissionDenied(
                "Only OWNER can update roles"
            )

        target_membership = (
            HomeMemberRepository.get_membership(
                home=home,
                user=target_user,
            )
        )

        if not target_membership:
            raise Exception("Member not found")

        permissions = (
            HomeMemberService.get_role_permissions(role)
        )

        return HomeMemberRepository.update_role(
            membership=target_membership,
            role=role,
            permissions=permissions,
        )

    @staticmethod
    def get_role_permissions(role):

        if role == Role.OWNER.value:
            return {
                "can_control_devices": True,
                "can_manage_members": True,
                "can_unlock_door": True,
                "receive_alerts": True,
            }

        if role == Role.ADMIN.value:
            return {
                "can_control_devices": True,
                "can_manage_members": True,
                "can_unlock_door": True,
                "receive_alerts": True,
            }

        return {
            "can_control_devices": False,
            "can_manage_members": False,
            "can_unlock_door": False,
            "receive_alerts": True,
        }