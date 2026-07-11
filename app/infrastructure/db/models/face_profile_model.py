#app/infrastructure/db/models/face_profile_model.py
import uuid
from django.db import models

from app.infrastructure.db.models.home_member_model import HomeMember


class FaceProfile(models.Model):
    """
    Stores facial embeddings for known users.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    home_member = models.ForeignKey(
        HomeMember,
        on_delete=models.CASCADE,
        related_name="face_profiles",
    )

    label_name = models.CharField(max_length=255)

    # Store # Multiple embeddings grouped by pose
    # {
    #   "CENTER": [[512 floats], [512 floats]],
    #   "LEFT":   [[...], [...]],
    #   "RIGHT":  [[...]],
    #   "UP":     [[...]],
    #   "DOWN":   [[...]]
    # }
    embeddings = models.JSONField(
        default=dict
    )

    image_url = models.URLField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "devices"

    def __str__(self):
        if self.home_member:
            return f"{self.label_name} ({self.home_member.user.email})"
