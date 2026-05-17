from django.core.exceptions import PermissionDenied

from app.domain.value_objects.lock_status import (
    LockStatus,
)

from app.infrastructure.db.repositories.django_home_member_repository import (
    DjangoHomeMemberRepository,
)

from app.infrastructure.db.repositories.django_access_log_repository import (
    DjangoAccessLogRepository,
)


class SmartLockService:

    member_repository = DjangoHomeMemberRepository()

    access_log_repository = (
        DjangoAccessLogRepository()
    )

    @staticmethod
    def unlock_door(
        acting_user,
        home,
        smart_lock,
    ):

        membership = (
            SmartLockService.member_repository
            .get_membership(
                home=home,
                user=acting_user,
            )
        )

        if not membership:
            raise PermissionDenied(
                "Not home member"
            )

        if not membership.can_unlock_door:

            (
                SmartLockService.access_log_repository
                .create_log(
                    user=acting_user,
                    device=smart_lock.device,
                    action="unlock_attempt",
                    result="failed",
                    message="No permission",
                )
            )

            raise PermissionDenied(
                "No unlock permission"
            )

        smart_lock.status = (
            LockStatus.UNLOCKED.value
        )

        smart_lock.last_unlocked_by = (
            acting_user.email
        )

        smart_lock.save()

        (
            SmartLockService.access_log_repository
            .create_log(
                user=acting_user,
                device=smart_lock.device,
                action="unlock_door",
                result="success",
                message="Door unlocked",
            )
        )

        return smart_lock