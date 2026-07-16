from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.domain.entities.detection_event import DetectionEvent


class DetectionEventRepository(ABC):
    @abstractmethod
    def create(self, event: DetectionEvent) -> DetectionEvent: ...

    @abstractmethod
    def update(self, event: DetectionEvent) -> DetectionEvent: ...

    @abstractmethod
    def find_recent_open_event(
        self, device_id, identity_key: str, since: datetime
    ) -> Optional[DetectionEvent]:
        """
        Find an event for this device+identity whose last_seen_at is after `since`.
        This is the dedup lookup — one query, indexed on (device_id, last_seen_at).
        """
        ...