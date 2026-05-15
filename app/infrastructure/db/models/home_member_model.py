import uuid

from django.conf import settings
from django.db import models

from app.domain.value_objects.role import Role
from app.infrastructure.db.models.home_model import Home


class HomeMember(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="home_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )

    can_view_dashboard = models.BooleanField(default=True)

    can_control_devices = models.BooleanField(default=False)

    can_manage_members = models.BooleanField(default=False)

    can_unlock_door = models.BooleanField(default=False)

    receive_alerts = models.BooleanField(default=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "homes"
        unique_together = ("home", "user")

    def __str__(self):
        return f"{self.user.email} - {self.home.name}"