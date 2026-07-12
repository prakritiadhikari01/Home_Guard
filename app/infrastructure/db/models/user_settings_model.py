from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    # Notifications
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)

    # Appearance
    dark_mode = models.BooleanField(default=True)

    # Time
    timezone = models.CharField(max_length=50, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        
    def __str__(self):
        return f"{self.user.full_name} Settings"