import uuid
from django.db import models
from django.conf import settings

from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.home_model import Home


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
        null=True,
        blank=True
    )

    label_name = models.CharField(max_length=255)

    # Store embedding as JSON list of floats
    embedding = models.JSONField()

    image_url = models.URLField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "devices"

    def __str__(self):
        if self.home_member:
            return f"{self.label_name} ({self.home_member.user.email})"

        return self.label_name