#app/infrastructure/db/models/device_model.py
import uuid

from django.db import models

from app.infrastructure.db.models.home_model import Home

from app.domain.value_objects.device_type import DeviceType
from app.domain.value_objects.device_status import DeviceStatus

class Device(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices",
    )

    name = models.CharField(
        max_length=255,
    )

    device_type = models.CharField(
        max_length=50,
        choices=DeviceType.choices(),
    )

    ip_address = models.CharField(
        max_length=255,
    )
    stream_url = models.URLField(
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices(),
        default=DeviceStatus.ONLINE.value,
    )

    last_active = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        app_label = "devices"

    def __str__(self):
        return self.name