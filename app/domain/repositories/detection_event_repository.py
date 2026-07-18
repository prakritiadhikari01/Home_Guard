from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.entities.detection_event import DetectionEvent


class DetectionEventRepository(ABC):
    @abstractmethod
    def create(self, event: DetectionEvent) -> DetectionEvent: ...

    @abstractmethod
    def update(self, event: DetectionEvent) -> DetectionEvent: ...

    @abstractmethod
    def find_recent_open_event(
        self, device_id, person_type: str, face_profile_id, since: datetime
    ) -> Optional[DetectionEvent]:
        """
        Find an event for this device+identity whose timestamp is after `since`.
        This is the dedup lookup — one query, indexed on (device, person_type, matched_face, timestamp).
        """
        ...

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        """Fetch a single event by id. Used by the enrichment step."""
        ...

    @abstractmethod
    def update_enrichment(
        self,
        event_id: UUID,
        clip_url: Optional[str],
        thumbnail_url: Optional[str],
        event_summary: Optional[str],
        extra_metadata: Optional[dict],
    ) -> Optional[DetectionEvent]:
        """
        Attach the slower, VLM-derived fields to an already-created event.
        Merges extra_metadata into the existing metadata rather than replacing it.
        Returns None if no event with that id exists.
        """
        ...
