import uuid

from django.db import models

from django.conf import settings

from app.infrastructure.db.models.home_model import Home

from app.domain.value_objects.role import Role


class HomeInvitation(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="invitations"
    )

    invited_email = models.EmailField()

    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending","Pending"),
            ("accepted","Accepted"),
            ("rejected","Rejected"),
        ],
        default="pending"
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        app_label = "homes"

    def __str__(self):
        return f"{self.invited_email} -> {self.home.name}"