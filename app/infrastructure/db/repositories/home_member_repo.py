from app.infrastructure.db.models.home_member_model import HomeMember


class HomeMemberRepository:

    @staticmethod
    def get_membership(home, user):
        return HomeMember.objects.filter(
            home=home,
            user=user,
        ).first()

    @staticmethod
    def member_exists(home, user):
        return HomeMember.objects.filter(
            home=home,
            user=user,
        ).exists()

    @staticmethod
    def create_member(**kwargs):
        return HomeMember.objects.create(**kwargs)

    @staticmethod
    def get_home_members(home):
        return HomeMember.objects.filter(
            home=home
        ).select_related("user")

    @staticmethod
    def remove_member(home, user):
        membership = HomeMember.objects.filter(
            home=home,
            user=user,
        ).first()

        if membership:
            membership.delete()

        return membership

    @staticmethod
    def update_role(membership, role, permissions):
        membership.role = role

        membership.can_control_devices = permissions["can_control_devices"]
        membership.can_manage_members = permissions["can_manage_members"]
        membership.can_unlock_door = permissions["can_unlock_door"]
        membership.receive_alerts = permissions["receive_alerts"]

        membership.save()

        return membership