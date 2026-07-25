from typing import Optional
from uuid import UUID
from django.utils import timezone

from app.domain.entities.alerts import Alert
from app.domain.repositories.alert_repository import AlertRepository
from app.infrastructure.db.models.alerts_model import Alert as AlertModel


class DjangoAlertRepository(AlertRepository):

    def create_if_not_exists(self, alert: Alert) -> Alert:
        model, _created = AlertModel.objects.get_or_create(
            event_id=alert.event_id,
            reason=alert.reason,
            defaults={
                "home_id": alert.home_id,
                "severity": alert.severity,
            },
        )
        return self._to_entity(model)

    def list_active(self, home_id: UUID) -> list[Alert]:
        qs = AlertModel.objects.filter(home_id=home_id, status="ACTIVE").order_by("-created_at")
        return [self._to_entity(m) for m in qs]

    def resolve(self, alert_id: UUID, resolved_by_id: Optional[int]) -> Optional[Alert]:
        model = AlertModel.objects.filter(id=alert_id).first()
        if model is None:
            return None
        model.status = "RESOLVED"
        model.resolved_by_id = resolved_by_id
        model.resolved_at = timezone.now()
        model.save(update_fields=["status", "resolved_by_id", "resolved_at"])
        return self._to_entity(model)

    def dismiss(self, alert_id: UUID) -> Optional[Alert]:
        model = AlertModel.objects.filter(id=alert_id).first()
        if model is None:
            return None
        model.status = "DISMISSED"
        model.save(update_fields=["status"])
        return self._to_entity(model)

    def _to_entity(self, model) -> Alert:
        return Alert(
            id=model.id,
            home_id=model.home_id,
            event_id=model.event_id,
            severity=model.severity,
            reason=model.reason,
            status=model.status,
            resolved_by_id=model.resolved_by_id,
            resolved_at=model.resolved_at,
            created_at=model.created_at,
        )