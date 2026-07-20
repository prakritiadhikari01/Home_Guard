# app/application/services/enrollment_service.py
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from app.domain.value_objects.enrollment_status import EnrollmentStatus
from app.infrastructure.db.repositories.django_enrollment_repository import DjangoEnrollmentRepository
from app.infrastructure.db.repositories.django_face_profile_repository import DjangoFaceProfileRepository


class EnrollmentService:

    enrollment_repository = DjangoEnrollmentRepository()
    face_repository = DjangoFaceProfileRepository()

    @staticmethod
    @transaction.atomic
    def start_enrollment(user, invitation=None):
        """One pending session per user at a time — reused if the user
        double-clicks 'scan' or refreshes the page."""

        existing_session = EnrollmentService.enrollment_repository.get_pending_session_for_user(user)
        if existing_session:
            return existing_session

        return EnrollmentService.enrollment_repository.create_session(
            user=user,
            invitation=invitation,
        )

    @staticmethod
    def get_status(session_id):
        session = EnrollmentService.enrollment_repository.get_by_id(session_id)
        if not session:
            raise NotFound("Enrollment session not found.")
        return session

    @staticmethod
    @transaction.atomic
    def complete_enrollment(session_id, embeddings):
        session = EnrollmentService.enrollment_repository.get_by_id(session_id)
        if not session:
            raise NotFound("Enrollment session not found.")

        if session.status == EnrollmentStatus.COMPLETED.value:
            raise ValidationError("Enrollment already completed.")

        user = session.user
        label_name = user.full_name

        # One profile per user — create on first enrollment, update on re-enrollment.
        face_profile = EnrollmentService.face_repository.create_or_update_for_user(
            user=user,
            label_name=label_name,
            embeddings=embeddings,
            is_verified=True,
        )

        EnrollmentService.enrollment_repository.mark_completed(session)

        return {"session": session, "face_profile": face_profile}

    @staticmethod
    @transaction.atomic
    def fail_enrollment(session_id, reason):
        session = EnrollmentService.enrollment_repository.get_by_id(session_id)
        if not session:
            raise NotFound("Enrollment session not found.")
        return EnrollmentService.enrollment_repository.mark_failed(session, reason)