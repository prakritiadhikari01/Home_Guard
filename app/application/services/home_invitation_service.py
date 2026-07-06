from django.core.exceptions import PermissionDenied
from django.db import transaction

from rest_framework.exceptions import ValidationError

from app.domain.services.access_policy import AccessPolicy

from app.infrastructure.db.repositories.django_home_member_repository import (
    DjangoHomeMemberRepository,
)
from app.infrastructure.db.repositories.django_home_invitation_repository import (
    DjangoHomeInvitationRepository,
)


class HomeInvitationService:

    invitation_repository = DjangoHomeInvitationRepository()
    member_repository = DjangoHomeMemberRepository()

    @staticmethod
    @transaction.atomic
    def send_invitation(
        acting_user,
        home,
        email,
        role,
        permissions,
    ):

        acting_membership = (
            HomeInvitationService.member_repository.get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not AccessPolicy.is_owner(
            acting_membership
        ):
            raise PermissionDenied(
                "Only OWNER can invite members."
            )

        if acting_user.email == email:
            raise ValidationError(
                "You cannot invite yourself."
            )

        existing_pending = (
            HomeInvitationService.invitation_repository
            .get_pending_invitation(
                home,
                email,
            )
        )

        if existing_pending:
            raise ValidationError(
                "Invitation already pending."
            )

        existing_user = (
            HomeInvitationService.invitation_repository
            .get_user_by_email(
                email
            )
        )

        if existing_user:

            existing_member = (
                HomeInvitationService.member_repository
                .get_membership(
                    home=home,
                    user=existing_user,
                )
            )

            if existing_member:
                raise ValidationError(
                    "User is already a member of this home."
                )

        return (
            HomeInvitationService.invitation_repository
            .create_invitation(
                home=home,
                email=email,
                invited_by=acting_user,
                role=role,
                permissions=permissions,
            )
        )

    @staticmethod
    @transaction.atomic
    def accept_invitation(
        invitation,
        user,
    ):

        invitation = (
            HomeInvitationService.invitation_repository.accept(
                invitation
            )
        )

        permissions = invitation.permissions

        membership = (
            HomeInvitationService.member_repository.create_member(
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

        (
            HomeInvitationService.invitation_repository
            .delete_other_pending(
                home=invitation.home,
                email=user.email,
                invitation_id=invitation.id,
            )
        )

        return membership

    @staticmethod
    @transaction.atomic
    def reject_invitation(
        invitation,
    ):

        return (
            HomeInvitationService.invitation_repository.reject(
                invitation
            )
        )

    @staticmethod
    def get_pending_invitations(
        user,
    ):

        return (
            HomeInvitationService.invitation_repository
            .get_pending_invitations(
                user
            )
        )