import uuid

from django.db import models

from app.infrastructure.db.models.device_model import Device

from app.domain.value_objects.lock_status import LockStatus
from app.infrastructure.db.models.home_member_model import (
    HomeMember
)

class SmartLock(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="smart_lock",
    )

    status = models.CharField(
        max_length=20,
        choices=LockStatus.choices(),
        default=LockStatus.LOCKED.value,
    )

    last_unlocked_by = models.ForeignKey(
        HomeMember,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unlock_events"
    )
    
    last_unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "devices"