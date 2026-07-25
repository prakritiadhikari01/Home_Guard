from celery import shared_task

from app.application.services.smart_lock_service import SmartLockService


@shared_task
def verify_and_unlock_task(smart_lock_id, verification_id):
    SmartLockService.resolve_unlock_attempt(
        smart_lock_id=smart_lock_id,
        verification_id=verification_id,
    )


@shared_task
def auto_relock_task(smart_lock_id, verification_id):
    SmartLockService.auto_relock(
        smart_lock_id=smart_lock_id,
        verification_id=verification_id,
    )