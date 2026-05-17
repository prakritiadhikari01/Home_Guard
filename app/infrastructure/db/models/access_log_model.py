import uuid

from django.db import models
from django.conf import settings

from app.infrastructure.db.models.device_model import Device


class AccessLog(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
    )

    action = models.CharField(
        max_length=255,
    )

    result = models.CharField(
        max_length=255,
    )

    message = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        app_label = "devices"