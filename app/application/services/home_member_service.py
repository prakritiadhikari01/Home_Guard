from django.core.exceptions import PermissionDenied

from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.repositories.home_repo import HomeRepository
from app.domain.value_objects.role import Role


class HomeMemberService:

    @staticmethod
    def add_member(
        acting_user,
        home,
        target_user,
        role=Role.MEMBER.value,
    ):

        # check if acting user is OWNER
        membership = HomeMember.objects.filter(
            home=home,
            user=acting_user,
        ).first()

        if not membership:
            raise PermissionDenied("You are not a member of this home")

        if membership.role != Role.OWNER.value:
            raise PermissionDenied("Only OWNER can add members")

        # prevent duplicate members
        existing_member = HomeMember.objects.filter(
            home=home,
            user=target_user,
        ).exists()

        if existing_member:
            raise Exception("User already exists in home")

        permissions = HomeMemberService.get_role_permissions(role)

        return HomeRepository.create_home_member(
            home=home,
            user=target_user,
            role=role,
            **permissions
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