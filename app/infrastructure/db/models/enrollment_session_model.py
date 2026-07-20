# app/infrastructure/db/models/enrollment_session_model.py
import uuid
from django.conf import settings
from django.db import models

from app.infrastructure.db.models.home_invitation_model import HomeInvitation
from app.domain.value_objects.enrollment_status import EnrollmentStatus


class EnrollmentSession(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # NEW: the session is now about a USER, not an invitation.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollment_sessions",
    )

    # invitation becomes optional context (only set when triggered by an invite).
    invitation = models.ForeignKey(
        HomeInvitation,
        on_delete=models.CASCADE,
        related_name="enrollment_sessions",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices(),
        default=EnrollmentStatus.PENDING.value,
    )

    ai_engine = models.CharField(max_length=100, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        app_label = "devices"

    def __str__(self):
        email = self.user.email if self.user else "No User"
        return f"{email} - {self.status}"