from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.entities.detection_event import DetectionEvent


class DetectionEventRepository(ABC):

    @abstractmethod
    def find_open_by_track(self, device_id: UUID, track_id: str) -> Optional[DetectionEvent]:
        """The real dedup lookup — (device_id, track_id, status=OPEN)."""
        ...

    @abstractmethod
    def create(self, event: DetectionEvent) -> DetectionEvent:
        """Persists a brand new OPEN session."""
        ...

    @abstractmethod
    def update_progress(self, event: DetectionEvent) -> DetectionEvent:
        """
        Merge-updates classification/confidence/media fields on an OPEN
        session. Must never touch clip_url/event_summary/is_enriched —
        those belong to attach_enrichment().
        """
        ...

    @abstractmethod
    def close_session(
        self, event_id: UUID, ended_at: datetime, duration_seconds: int
    ) -> Optional[DetectionEvent]:
        ...

    @abstractmethod
    def attach_enrichment(
        self,
        event_id: UUID,
        clip_url: Optional[str],
        thumbnail_url: Optional[str],
        event_summary: Optional[str],
        extra_metadata: Optional[dict],
    ) -> Optional[DetectionEvent]:
        ...

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        ...

    @abstractmethod
    def find_stale_open_sessions(self, older_than: datetime) -> list[DetectionEvent]:
        """Used by the Celery beat sweep — safety net for sessions the AI
        engine never explicitly closed (crash / network drop)."""
        ...

    @abstractmethod
    def count_recent_unknown(self, device_id: UUID, since: datetime) -> int:
        """Used by alert evaluation for REPEATED_UNKNOWN."""
        ...
