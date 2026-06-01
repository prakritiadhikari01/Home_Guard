# app/application/services/smart_lock_service.py

from django.utils import timezone

from app.domain.services.access_policy import (
    AccessPolicy
)

from app.infrastructure.db.models.smart_lock_model import (
    SmartLock
)

from app.domain.value_objects.lock_status import (
    LockStatus
)


class SmartLockService:

    @staticmethod
    def auto_unlock(
        *,
        member,
        device
    ):

        membership = member

        if not AccessPolicy.can_unlock_door(
            membership
        ):
            return None

        smart_lock = SmartLock.objects.get(
            device=device
        )

        smart_lock.status = (
            LockStatus.UNLOCKED.value
        )

        smart_lock.last_unlocked_by = (
            membership
        )

        smart_lock.last_unlocked_at = (
            timezone.now()
        )

        smart_lock.save()

        return smart_lock