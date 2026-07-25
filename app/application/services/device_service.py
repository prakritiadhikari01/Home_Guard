# app/application/services/device_service.py
from django.core.exceptions import PermissionDenied
from app.infrastructure.db.models.smart_lock_model import SmartLock
from app.domain.value_objects.lock_status import LockStatus
from app.domain.value_objects.device_type import (
    DeviceType,
)
from app.infrastructure.db.models.detection_event_model import DetectionEvent
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.repositories.django_device_repository import (
    DjangoDeviceRepository,
)

from app.infrastructure.db.repositories.django_home_member_repository import (
    AbstractHomeMemberRepository,
)

from app.infrastructure.db.repositories.django_smart_lock_repository import (
    DjangoSmartLockRepository,
)
from app.infrastructure.external.ai_client import AIClient

class DeviceService:
    def __init__(self, member_repository: AbstractHomeMemberRepository):
        self.member_repository = member_repository

    device_repository = DjangoDeviceRepository()

    smart_lock_repository = DjangoSmartLockRepository()

    @staticmethod
    def _get_membership_or_raise(acting_user, home, require_control=True):
        membership = HomeMember.objects.filter(home=home, user=acting_user).first()

        if not membership:
            raise PermissionDenied("Not home member")

        if require_control and not membership.can_control_devices:
            raise PermissionDenied("No permission")

        return membership

    @staticmethod
    def _require_membership(acting_user, home):
        """
        Read-only guard: confirms the acting user belongs to this home,
        without requiring can_control_devices. Use this on GET views
        (device list/detail/health/events/settings) so any member can
        view devices, while register/edit/delete/restart still require
        can_control_devices via _get_membership_or_raise.
        """
        membership = HomeMember.objects.filter(home=home, user=acting_user).first()

        if not membership:
            raise PermissionDenied("Not home member")

        return membership

    @staticmethod
    def register_device(
        acting_user,
        home,
        validated_data,
    ):
        DeviceService._get_membership_or_raise(acting_user, home)

        device = DeviceService.device_repository.create_device(
            home=home,
            **validated_data,
        )

        # Automatically create SmartLock for smart lock devices
        if device.device_type == DeviceType.SMART_LOCK.value:
            SmartLock.objects.get_or_create(
                device=device,
                defaults={
                    "status": LockStatus.LOCKED.value,
                },
            )

        try:
            AIClient().register_device(device)
        except Exception:
            pass

        return device
    
    @staticmethod
    def get_home_devices(home):

        return (
            DeviceService.device_repository
            .get_home_devices(home)
        )
    
    @staticmethod
    def get_device(home, device_id):
        device = DeviceService.device_repository.get_device_by_id(device_id)
        if not device or device.home_id != home.id:
            return None
        return device

    @staticmethod
    def update_device(acting_user, home, device, data):
        DeviceService._get_membership_or_raise(acting_user, home)
        return DeviceService.device_repository.update_device(device, data)

    @staticmethod
    def delete_device(acting_user, home, device):
        DeviceService._get_membership_or_raise(acting_user, home)

        try:
            AIClient().remove_device(device)
        except Exception:
            pass

        DeviceService.device_repository.delete_device(device)

    @staticmethod
    def restart_device(acting_user, home, device):
        DeviceService._get_membership_or_raise(acting_user, home)

        # Let this one raise — if the engine can't restart the device,
        # the caller needs to know it failed.
        AIClient().restart_device(device)
        return device
    


# Device_health_service
class DeviceHealthService:

    @staticmethod
    def get_health(device):
        """
        DB knows last-known status; the AI engine knows what's happening
        right now (latency, fps, whether it's actually analyzing frames).
        """
        ai_status = {}
        try:
            # TODO: confirm this matches your real AIClient method.
            ai_status = AIClient().get_device_status(device) or {}
        except Exception:
            ai_status = {}

        return {
            "status": device.status,
            "last_active": device.last_active,
            "latency_ms": ai_status.get("latency_ms"),
            "fps": ai_status.get("fps"),
            "ai_running": ai_status.get("ai_running", False),
            "engine_connected": ai_status.get("engine_connected", False),
        }

class DeviceEventQueryService:

    @staticmethod
    def get_recent_events(device, limit=20):
        # NOTE: adjust field names if your DetectionEvent model differs.
        return (
            DetectionEvent.objects
            .filter(device=device)
            .order_by("-created_at")[:limit]
        )