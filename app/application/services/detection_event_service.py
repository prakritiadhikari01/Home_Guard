from typing import Optional
from uuid import UUID
from app.domain.services.event_orchestrator import EventOrchestrator
from app.domain.entities.detection_event import DetectionEvent
from app.domain.repositories.detection_event_repository import DetectionEventRepository


class DetectionEventService:
    def __init__(self, orchestrator: EventOrchestrator, repository: DetectionEventRepository):
        self.orchestrator = orchestrator
        self.repository = repository

    def ingest(self, validated_data: dict) -> DetectionEvent:
        """
        Fast path — called on every processed frame that produces a detection.
        No clip/summary here; those come later via enrich(). Keep this cheap.
        """
        incoming = DetectionEvent(
            id=None,
            home_id=validated_data["home_id"],
            device_id=validated_data["device_id"],
            event_type=validated_data["event_type"],
            person_type=validated_data["person_type"],
            person_label=validated_data.get("person_label"),
            member_id=validated_data.get("member_id"),
            face_profile_id=validated_data.get("face_profile_id"),
            confidence_score=validated_data.get("confidence_score", 0.0),
            camera_location=validated_data.get("camera_location"),
            image_url=validated_data.get("image_url"),
            snapshot_url=validated_data.get("snapshot_url"),
            thumbnail_url=validated_data.get("thumbnail_url"),
            timestamp=validated_data["timestamp"],
            duration_seconds=0,
            metadata={},
        )
        return self.orchestrator.process_detection(incoming)

    def enrich(self, event_id: UUID, validated_data: dict) -> Optional[DetectionEvent]:
        """
        Slow path — called by the AI engine once it has run the VLM pass on the
        clip for this event. Attaches clip_url / thumbnail_url / event_summary.
        Returns None if the event_id doesn't exist (view turns that into a 404).
        """
        return self.repository.update_enrichment(
            event_id=event_id,
            clip_url=validated_data.get("clip_url"),
            thumbnail_url=validated_data.get("thumbnail_url"),
            event_summary=validated_data.get("event_summary"),
            extra_metadata=validated_data.get("attributes"),
        )
