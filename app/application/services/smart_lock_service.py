# app/application/services/smart_lock_service.py
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from app.domain.services.access_policy import AccessPolicy
from app.infrastructure.db.models.smart_lock_model import SmartLock
from app.infrastructure.db.models.home_member_model import HomeMember
from app.domain.value_objects.lock_status import LockStatus
from app.infrastructure.external.ai_client import AIClient


class SmartLockService:

    @staticmethod
    def auto_unlock(*, member, device):

        smart_lock = SmartLock.objects.get(device=device)

        smart_lock.status = LockStatus.UNLOCKED.value
        smart_lock.last_unlocked_by = member
        smart_lock.last_unlocked_at = timezone.now()

        smart_lock.save()

        return smart_lock

    @staticmethod
    def manual_unlock(*, acting_user, device):
        membership = HomeMember.objects.filter(
            home=device.home,
            user=acting_user,
        ).first()

        if not membership:
            raise PermissionDenied("Not home member")

        if not AccessPolicy.can_unlock_door(membership):
            raise PermissionDenied("Not allowed to unlock this door")

        smart_lock = SmartLock.objects.select_related("device").get(device=device)

        result = AIClient().request_unlock(
            smart_lock=smart_lock,
            membership=membership,
        )

        return result

    @staticmethod
    def manual_lock(*, acting_user, device):
        membership = HomeMember.objects.filter(home=device.home, user=acting_user).first()

        if not membership or not membership.can_control_devices:
            raise PermissionDenied("Not allowed to lock this door")

        smart_lock = SmartLock.objects.get(device=device)
        smart_lock.status = LockStatus.LOCKED.value
        smart_lock.save()
        return smart_lock

    @staticmethod
    def get_lock_detail(device):
        return SmartLock.objects.select_related("last_unlocked_by").get(device=device)