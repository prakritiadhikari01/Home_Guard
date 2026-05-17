from app.domain.repositories.home_member_repository import (
    AbstractHomeMemberRepository,
)

from app.infrastructure.db.models.home_member_model import HomeMember


class DjangoHomeMemberRepository(
    AbstractHomeMemberRepository
):

    def get_membership(self, home, user):
        return HomeMember.objects.filter(
            home=home,
            user=user,
        ).first()

    def member_exists(self, home, user):
        return HomeMember.objects.filter(
            home=home,
            user=user,
        ).exists()

    def create_member(self, **kwargs):
        return HomeMember.objects.create(**kwargs)

    def get_home_members(self, home):
        return (
            HomeMember.objects
            .filter(home=home)
            .select_related("user")
            .order_by("-joined_at")
        )

    def remove_member(self, home, user):

        membership = (
            HomeMember.objects.filter(
                home=home,
                user=user,
            ).first()
        )

        if not membership:
            return None

        membership.delete()

        return True

    def update_role(
        self,
        membership,
        role,
        permissions,
    ):

        membership.role = role

        membership.can_control_devices = (
            permissions["can_control_devices"]
        )

        membership.can_manage_members = (
            permissions["can_manage_members"]
        )

        membership.can_unlock_door = (
            permissions["can_unlock_door"]
        )

        membership.receive_alerts = (
            permissions["receive_alerts"]
        )

        membership.save()

        return membership