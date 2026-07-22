from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.services.event_orchestrator import EventOrchestrator
from app.domain.entities.detection_event import DetectionEvent
from app.domain.repositories.detection_event_repository import DetectionEventRepository


class DetectionEventService:
    def __init__(self, orchestrator: EventOrchestrator, repository: DetectionEventRepository):
        self.orchestrator = orchestrator
        self.repository = repository

    def open(self, data: dict) -> DetectionEvent:
        """POST /events/open/ — motion + tracking assigns a track_id."""
        now = data.get("started_at") or datetime.utcnow()
        incoming = DetectionEvent(
            id=None,
            home_id=data["home_id"],
            device_id=data["device_id"],
            track_id=data["track_id"],
            status="OPEN",
            pipeline_stage=data.get("pipeline_stage", "MOTION_DETECTED"),
            event_type=data.get("event_type", "MOTION_DETECTED"),
            person_type=data.get("person_type", "UNKNOWN"),
            person_label=data.get("person_label"),
            member_id=data.get("member_id"),
            face_profile_id=data.get("face_profile_id"),
            confidence_score=data.get("confidence_score", 0.0),
            camera_location=data.get("camera_location"),
            image_url=data.get("image_url"),
            snapshot_url=data.get("snapshot_url"),
            thumbnail_url=data.get("thumbnail_url"),
            started_at=now,
            last_seen_at=now,
            timestamp=now,
            metadata=data.get("metadata", {}),
        )
        return self.orchestrator.open_session(incoming)

    def progress(self, event_id: UUID, data: dict) -> Optional[DetectionEvent]:
        """PATCH /events/<id>/progress/ — called repeatedly as recognition resolves."""
        incoming = DetectionEvent(
            id=None,
            home_id=data.get("home_id"),
            device_id=data.get("device_id"),
            track_id=data.get("track_id", ""),
            status="OPEN",
            pipeline_stage=data.get("pipeline_stage", "MOTION_DETECTED"),
            event_type=data.get("event_type", "MOTION_DETECTED"),
            person_type=data.get("person_type", "UNKNOWN"),
            person_label=data.get("person_label"),
            member_id=data.get("member_id"),
            face_profile_id=data.get("face_profile_id"),
            confidence_score=data.get("confidence_score", 0.0),
            image_url=data.get("image_url"),
            snapshot_url=data.get("snapshot_url"),
            thumbnail_url=data.get("thumbnail_url"),
            last_seen_at=data.get("last_seen_at") or datetime.utcnow(),
            metadata=data.get("metadata", {}),
        )
        return self.orchestrator.update_progress(event_id, incoming)

    def close(self, event_id: UUID, data: dict) -> Optional[DetectionEvent]:
        """PATCH /events/<id>/close/ — track lost."""
        ended_at = data.get("ended_at") or datetime.utcnow()
        return self.orchestrator.close_session(event_id, ended_at)

    def enrich(self, event_id: UUID, validated_data: dict) -> Optional[DetectionEvent]:
        """PATCH /events/<id>/enrich/ — Celery summary worker, unchanged contract."""
        return self.orchestrator.attach_enrichment(
            event_id=event_id,
            clip_url=validated_data.get("clip_url"),
            thumbnail_url=validated_data.get("thumbnail_url"),
            event_summary=validated_data.get("event_summary"),
            extra_metadata=validated_data.get("attributes"),
        )

    def sweep_stale(self) -> int:
        return self.orchestrator.sweep_stale_sessions()
