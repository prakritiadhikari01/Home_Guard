from django.utils import timezone

from app.domain.value_objects.enrollment_status import EnrollmentStatus
from app.infrastructure.db.models.enrollment_session_model import EnrollmentSession


class DjangoEnrollmentRepository:

    @staticmethod
    def create_session(user, invitation=None, ai_engine="windows-ai-engine"):
        return EnrollmentSession.objects.create(
            user=user,
            invitation=invitation,
            ai_engine=ai_engine,
            status=EnrollmentStatus.PENDING.value,
        )

    @staticmethod
    def get_by_id(session_id):
        return (
            EnrollmentSession.objects
            .select_related("user", "invitation", "invitation__home", "invitation__invited_by")
            .filter(id=session_id)
            .first()
        )

    @staticmethod
    def get_pending_session_for_user(user):
        return (
            EnrollmentSession.objects.filter(
                user=user,
                status__in=[
                    EnrollmentStatus.PENDING.value,
                    EnrollmentStatus.RUNNING.value,
                ],
            )
            .order_by("-started_at")
            .first()
        )

    @staticmethod
    def mark_running(session):
        session.status = EnrollmentStatus.RUNNING.value
        session.save(update_fields=["status"])
        return session

    @staticmethod
    def mark_completed(session):
        session.status = EnrollmentStatus.COMPLETED.value
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at"])
        return session

    @staticmethod
    def mark_failed(session, reason):
        session.status = EnrollmentStatus.FAILED.value
        session.failure_reason = reason
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "failure_reason", "completed_at"])
        return session

    @staticmethod
    def delete(session):
        session.delete()