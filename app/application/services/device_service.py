from django.core.exceptions import PermissionDenied

from app.domain.value_objects.device_type import (
    DeviceType,
)

from app.infrastructure.db.repositories.django_device_repository import (
    DjangoDeviceRepository,
)

from app.infrastructure.db.repositories.django_home_member_repository import (
    AbstractHomeMemberRepository,
)

from app.infrastructure.db.repositories.django_smart_lock_repository import (
    DjangoSmartLockRepository,
)


class DeviceService:
    def __init__(self, member_repository: AbstractHomeMemberRepository):
        self.member_repository = member_repository

    device_repository = DjangoDeviceRepository()

    smart_lock_repository = DjangoSmartLockRepository()

    @staticmethod
    def register_device(
        acting_user,
        home,
        validated_data,
    ):

        membership = (
            DeviceService.member_repository
            .get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not membership:
            raise PermissionDenied(
                "Not home member"
            )

        if not membership.can_control_devices:
            raise PermissionDenied(
                "No permission"
            )

        device = (
            DeviceService.device_repository
            .create_device(
                home=home,
                **validated_data,
            )
        )

        if (
            device.device_type
            == DeviceType.SMART_LOCK.value
        ):
            (
                DeviceService.smart_lock_repository
                .create_lock(
                    device=device,
                )
            )

        return device

    @staticmethod
    def get_home_devices(home):

        return (
            DeviceService.device_repository
            .get_home_devices(home)
        )