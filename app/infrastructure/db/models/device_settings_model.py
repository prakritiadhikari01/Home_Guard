import uuid

from django.db import models

from app.infrastructure.db.models.device_model import Device


class DeviceSettings(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    recording_enabled = models.BooleanField(
        default=True,
    )

    ai_enabled = models.BooleanField(
        default=True,
    )

    motion_detection = models.BooleanField(
        default=True,
    )

    night_vision = models.BooleanField(
        default=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "devices"

    def __str__(self):
        return f"{self.device.name} Settings"