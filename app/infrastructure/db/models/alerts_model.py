import uuid

from django.db import models
from django.conf import settings

from app.domain.value_objects.alerts import AlertReason, AlertSeverity, AlertStatus
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.detection_event_model import DetectionEvent


class Alert(models.Model):
    """
    Spawned by alert evaluation at session close-time. Separate lifecycle
    from DetectionEvent (ACTIVE/RESOLVED/DISMISSED) so the Alerts page has
    real actionable state instead of a badge derived from a detection row.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="alerts")
    event = models.ForeignKey(
        DetectionEvent, on_delete=models.CASCADE, related_name="alerts",
    )

    severity = models.CharField(max_length=20, choices=AlertSeverity.choices())
    reason = models.CharField(max_length=50, choices=AlertReason.choices())
    status = models.CharField(
        max_length=20, choices=AlertStatus.choices(), default=AlertStatus.ACTIVE.value,
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["home", "status"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "reason"], name="uniq_alert_per_event_reason"
            ),
        ]

    def __str__(self):
        return f"{self.reason} | {self.severity} | {self.status}"
