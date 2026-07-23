from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=3,
    acks_late=True,
)
def verify_and_unlock_task(self, smart_lock_id, membership_id, verification_id):
    from app.application.services.smart_lock_service import SmartLockService
    try:
        SmartLockService.resolve_unlock_attempt(
            smart_lock_id=smart_lock_id,
            membership_id=membership_id,
            verification_id=verification_id,
        )
    except Exception as exc:
        logger.exception("verify_and_unlock_task failed for lock %s", smart_lock_id)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=3,
    acks_late=True,
)
def auto_relock_task(self, smart_lock_id, verification_id):
    from app.application.services.smart_lock_service import SmartLockService
    try:
        SmartLockService.auto_relock(
            smart_lock_id=smart_lock_id,
            verification_id=verification_id,
        )
    except Exception as exc:
        logger.exception("auto_relock_task failed for lock %s", smart_lock_id)
        raise self.retry(exc=exc)