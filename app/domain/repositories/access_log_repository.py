from app.infrastructure.db.models.access_log_model import AccessLog


class DjangoAccessLogRepository:

    def create_log(
        self,
        user,
        device,
        action,
        result,
        message=None,
        confidence_score=0.0,
        event_type=None,
    ):

        return AccessLog.objects.create(
            user=user,
            device=device,
            action=action,
            result=result,
            message=message,
            confidence_score=confidence_score,
            event_type=event_type,
        )