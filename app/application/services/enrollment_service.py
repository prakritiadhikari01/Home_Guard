#app/application/services/enrollment_service.py
from django.db import transaction

from rest_framework.exceptions import (
    NotFound,
    ValidationError,
)

from app.domain.value_objects.enrollment_status import (
    EnrollmentStatus,
)

from app.infrastructure.db.repositories.django_enrollment_repository import (
    DjangoEnrollmentRepository,
)

from app.infrastructure.db.repositories.django_face_profile_repository import (
    DjangoFaceProfileRepository,
)

from app.infrastructure.db.repositories.django_home_invitation_repository import (
    DjangoHomeInvitationRepository,
)

from app.infrastructure.db.repositories.django_home_member_repository import (
    DjangoHomeMemberRepository,
)


class EnrollmentService:

    enrollment_repository = DjangoEnrollmentRepository()

    invitation_repository = DjangoHomeInvitationRepository()

    member_repository = DjangoHomeMemberRepository()

    face_repository = DjangoFaceProfileRepository()

    @staticmethod
    @transaction.atomic
    def start_enrollment(
        invitation,
    ):

        existing_session = (
            EnrollmentService.enrollment_repository
            .get_pending_session(
                invitation
            )
        )

        if existing_session:
            return existing_session

        return (
            EnrollmentService.enrollment_repository
            .create_session(
                invitation=invitation
            )
        )

    @staticmethod
    def get_status(
        session_id,
    ):

        session = (
            EnrollmentService.enrollment_repository
            .get_by_id(
                session_id
            )
        )

        if not session:
            raise NotFound(
                "Enrollment session not found."
            )

        return session

    @staticmethod
    @transaction.atomic
    def complete_enrollment(
        session_id,
        embeddings,
    ):

        session = (
            EnrollmentService.enrollment_repository
            .get_by_id(session_id)
        )

        if not session:
            raise NotFound(
                "Enrollment session not found."
            )

        if (
            session.status
            == EnrollmentStatus.COMPLETED.value
        ):
            raise ValidationError(
                "Enrollment already completed."
            )

        invitation = session.invitation

        permissions = invitation.permissions

        user = (
            EnrollmentService.invitation_repository
            .get_user_by_email(
                invitation.email
            )
        )

        if not user:
            raise ValidationError(
                "Invited user does not exist."
            )

        label_name = user.full_name

        existing_member = (
            EnrollmentService.member_repository
            .get_membership(
                home=invitation.home,
                user=user,
            )
        )

        if existing_member:
            raise ValidationError(
                "User is already enrolled in this home."
            )

        membership = (
            EnrollmentService.member_repository
            .create_member(
                home=invitation.home,
                user=user,
                role=invitation.role,
                can_view_dashboard=True,
                can_control_devices=permissions.get(
                    "can_control_devices",
                    False,
                ),
                can_manage_members=permissions.get(
                    "can_manage_members",
                    False,
                ),
                can_unlock_door=permissions.get(
                    "can_unlock_door",
                    False,
                ),
                receive_alerts=permissions.get(
                    "receive_alerts",
                    True,
                ),
            )
        )

        existing_profile = (
            EnrollmentService.face_repository
            .get_by_home_member(
                membership
            )
        )

        if existing_profile:
            raise ValidationError(
                "Face profile already exists."
            )

        face_profile = (
            EnrollmentService.face_repository
            .create_face_profile(
                home_member=membership,
                label_name=label_name,
                embeddings=embeddings,
                is_verified=True,
            )
        )

        EnrollmentService.invitation_repository.accept(
            invitation
        )

        (
            EnrollmentService.invitation_repository
            .delete_other_pending(
                home=invitation.home,
                email=invitation.email,
                invitation_id=invitation.id,
            )
        )

        (
            EnrollmentService.enrollment_repository
            .mark_completed(session)
        )

        return {
            "session": session,
            "member": membership,
            "face_profile": face_profile,
        }
    
    
    @staticmethod
    @transaction.atomic
    def fail_enrollment(
        session_id,
        reason,
    ):

        session = (
            EnrollmentService.enrollment_repository
            .get_by_id(
                session_id
            )
        )

        if not session:
            raise NotFound(
                "Enrollment session not found."
            )

        return (
            EnrollmentService.enrollment_repository
            .mark_failed(
                session,
                reason,
            )
        )