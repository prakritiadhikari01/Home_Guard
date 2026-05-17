from app.infrastructure.db.models.smart_lock_model import (
    SmartLock,
)


class DjangoSmartLockRepository:

    @staticmethod
    def create_lock(**kwargs):
        return SmartLock.objects.create(**kwargs)

    @staticmethod
    def get_lock_by_id(lock_id):
        return SmartLock.objects.filter(
            id=lock_id
        ).first()