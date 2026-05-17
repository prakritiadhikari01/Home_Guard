from app.infrastructure.db.models.access_log_model import (
    AccessLog,
)


class DjangoAccessLogRepository:

    @staticmethod
    def create_log(**kwargs):
        return AccessLog.objects.create(**kwargs)