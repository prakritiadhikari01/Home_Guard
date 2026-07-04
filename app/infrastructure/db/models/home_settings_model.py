import uuid

from django.db import models

from app.domain.value_objects.security_mode import SecurityMode
from app.infrastructure.db.models.home_model import Home
from app.domain.value_objects.security_mode import SecurityMode

class HomeSettings(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.OneToOneField(
        Home,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    security_mode = models.CharField(
        max_length=20,
        choices=SecurityMode.choices(),
        default=SecurityMode.NORMAL.value,
    )

    confidence_threshold = models.PositiveIntegerField(
        default=80,
    )

    human_detection = models.BooleanField(default=True)

    animal_detection = models.BooleanField(default=True)

    vehicle_detection = models.BooleanField(default=True)

    motion_detection = models.BooleanField(default=True)

    ai_summary_digest = models.BooleanField(default=True)

    unknown_notify_owner = models.BooleanField(default=True)

    repeated_detection_alert = models.BooleanField(default=True)

    known_member_log_only = models.BooleanField(default=True)

    ignore_animals = models.BooleanField(default=False)

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "homes"

    def __str__(self):
        return f"Settings - {self.home.name}"