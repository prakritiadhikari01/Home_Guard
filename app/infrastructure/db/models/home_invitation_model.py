#app/infrastructure/db/models/home_invitation_model.py
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

    email = models.EmailField()

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_home_invitations",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )

    permissions = models.JSONField(default=dict)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending","Pending"),
            ("accepted","Accepted"),
            ("rejected","Rejected"),
        ],
        default="pending"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        app_label = "homes"

        constraints = [
            models.UniqueConstraint(
                fields=["home", "email"],
                condition=models.Q(status="pending"),
                name="unique_pending_home_invitation",
            )
        ]
        
    def __str__(self):
        return f"{self.email} -> {self.home.name}"