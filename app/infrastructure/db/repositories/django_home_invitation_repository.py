#app/infrastructure/db/repositories/django_home_invitation_repository.py
from django.contrib.auth import get_user_model

from app.infrastructure.db.models.home_invitation_model import (
    HomeInvitation,
)

User = get_user_model()


class DjangoHomeInvitationRepository:

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

    def get_pending_invitation(
        self,
        home,
        email,
    ):
        return HomeInvitation.objects.filter(
            home=home,
            email=email,
            status="pending",
        ).first()

    def get_pending_invitations(
        self,
        user,
    ):
        return (
            HomeInvitation.objects.filter(
                email=user.email,
                status="pending",
            )
            .select_related(
                "home",
                "invited_by",
            )
        )

    def accept(
        self,
        invitation,
    ):
        invitation.status = "accepted"
        invitation.save()
        return invitation

    def reject(
        self,
        invitation,
    ):
        invitation.status = "rejected"
        invitation.save()
        return invitation

    def delete_other_pending(
        self,
        home,
        email,
        invitation_id,
    ):
        HomeInvitation.objects.filter(
            home=home,
            email=email,
            status="pending",
        ).exclude(
            id=invitation_id,
        ).delete()

    def get_user_by_email(
        self,
        email,
    ):
        return User.objects.filter(
            email=email,
        ).first()