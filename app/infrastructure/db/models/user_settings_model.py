import uuid

from django.conf import settings
from django.db import models


class UserSettings(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    push_notifications = models.BooleanField(
        default=True,
    )

    email_notifications = models.BooleanField(
        default=True,
    )

    receive_daily_digest = models.BooleanField(
        default=True,
    )

    broadcast_house_alerts = models.BooleanField(
        default=False,
    )

    emergency_notifications = models.BooleanField(
        default=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "accounts"

    def __str__(self):
        return f"{self.user.email} Settings"