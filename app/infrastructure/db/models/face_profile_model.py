import uuid

from django.conf import settings
from django.db import models


class FaceProfile(models.Model):
    """
    Stores a user's facial embeddings.

    One user can have only one FaceProfile.
    This profile is shared across all homes the user belongs to.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="face_profile",
    )

    label_name = models.CharField(
        max_length=255,
    )

    # Example:
    # {
    #   "CENTER": [[512 floats], [512 floats]],
    #   "LEFT":   [[...], [...]],
    #   "RIGHT":  [[...]],
    #   "UP":     [[...]],
    #   "DOWN":   [[...]]
    # }
    embeddings = models.JSONField(
        default=dict,
    )

    image_url = models.URLField(
        null=True,
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "devices"

    def __str__(self):
        return f"{self.label_name} ({self.user.email})"