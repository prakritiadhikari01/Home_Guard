from datetime import timedelta
from typing import Optional
from app.domain.repositories.detection_event_repository import DetectionEventRepository
from app.domain.entities.detection_event import DetectionEvent

DUPLICATE_WINDOW_SECONDS = 30


class EventOrchestrator:
    def __init__(self, repository: DetectionEventRepository):
        self.repository = repository

    def process_detection(self, incoming: DetectionEvent) -> DetectionEvent:
        existing = self.repository.find_recent_open_event(
            device_id=incoming.device_id,
            person_type=incoming.person_type,
            face_profile_id=incoming.face_profile_id,
            since=incoming.timestamp - timedelta(seconds=DUPLICATE_WINDOW_SECONDS),
        )

        if existing:
            return self._merge(existing, incoming)

        return self.repository.create(incoming)

    def _merge(self, existing: DetectionEvent, incoming: DetectionEvent) -> DetectionEvent:
        elapsed = (incoming.timestamp - existing.timestamp).total_seconds()

        existing.duration_seconds += max(elapsed, 0)
        existing.timestamp = incoming.timestamp

        if incoming.confidence_score > existing.confidence_score:
            existing.confidence_score = incoming.confidence_score
            existing.image_url = incoming.image_url or existing.image_url
            existing.snapshot_url = incoming.snapshot_url or existing.snapshot_url
            existing.thumbnail_url = incoming.thumbnail_url or existing.thumbnail_url

        existing.metadata["occurrence_count"] = existing.metadata.get("occurrence_count", 1) + 1

        return self.repository.update(existing)