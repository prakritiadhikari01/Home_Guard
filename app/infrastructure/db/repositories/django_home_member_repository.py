#app/infrastructure/db/repositories/django_home_member_repository.py
from app.domain.repositories.home_member_repository import (
    AbstractHomeMemberRepository,
)

from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.home_invitation_model import (
    HomeInvitation,
)
from django.contrib.auth import get_user_model
User = get_user_model()
class DjangoHomeMemberRepository(
    AbstractHomeMemberRepository
):
    def create_invitation(
        self,
        home,
        email,
        invited_by,
        role,
        permissions,
    ):

        return HomeInvitation.objects.create(
            home=home,
            email=email,
            invited_by=invited_by,
            role=role,
            permissions=permissions,
        )
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
    
    #Invitations related methods 
    

    def get_pending_invitation(self, home, email):
        return HomeInvitation.objects.filter(
            home=home,
            email=email,
            status="pending",
        ).first()

    def get_user_by_email(self, email):
        return User.objects.filter(
            email=email
        ).first()