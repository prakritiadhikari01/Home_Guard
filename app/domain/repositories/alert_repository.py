from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.alerts import Alert



class AlertRepository(ABC):

    @abstractmethod
    def create_if_not_exists(self, alert: Alert) -> Alert:
        """
        Idempotent create keyed on (event_id, reason) — alert evaluation can
        be re-run safely (e.g. a retried close call) without duplicating
        alerts for the same session/reason.
        """
        ...

    @abstractmethod
    def list_active(self, home_id: UUID) -> list[Alert]:
        ...

    @abstractmethod
    def resolve(self, alert_id: UUID, resolved_by_id: Optional[int]) -> Optional[Alert]:
        ...

    @abstractmethod
    def dismiss(self, alert_id: UUID) -> Optional[Alert]:
        ...
