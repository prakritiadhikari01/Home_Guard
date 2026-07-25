from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.repositories.detection_event_repository import DetectionEventRepository
from app.domain.entities.detection_event import DetectionEvent
from app.infrastructure.db.models.detection_event_model import DetectionEvent as DetectionEventModel


class DjangoDetectionEventRepository(DetectionEventRepository):

    def find_open_by_track(self, device_id, track_id: str) -> Optional[DetectionEvent]:
        model = DetectionEventModel.objects.filter(
            device_id=device_id, track_id=track_id, status="OPEN",
        ).first()
        return self._to_entity(model) if model else None

    def create(self, event: DetectionEvent) -> DetectionEvent:
        model = DetectionEventModel.objects.create(
            home_id=event.home_id,
            device_id=event.device_id,
            track_id=event.track_id,
            status=event.status,
            pipeline_stage=event.pipeline_stage,
            event_type=event.event_type,
            person_type=event.person_type,
            person_label=event.person_label,
            matched_member_id=event.member_id,
            matched_face_id=event.face_profile_id,
            confidence_score=event.confidence_score,
            camera_location=event.camera_location,
            image_url=event.image_url,
            snapshot_url=event.snapshot_url,
            thumbnail_url=event.thumbnail_url,
            started_at=event.started_at,
            last_seen_at=event.last_seen_at,
            timestamp=event.timestamp or event.started_at,
            metadata=event.metadata,
        )
        return self._to_entity(model)

    def update_progress(self, event: DetectionEvent) -> DetectionEvent:
        # Deliberately does NOT touch clip_url / event_summary / is_enriched /
        # status / ended_at / duration_seconds — those belong to
        # close_session() and attach_enrichment().
        DetectionEventModel.objects.filter(id=event.id).update(
            pipeline_stage=event.pipeline_stage,
            event_type=event.event_type,
            person_type=event.person_type,
            person_label=event.person_label,
            matched_member_id=event.member_id,
            matched_face_id=event.face_profile_id,
            confidence_score=event.confidence_score,
            image_url=event.image_url,
            snapshot_url=event.snapshot_url,
            thumbnail_url=event.thumbnail_url,
            last_seen_at=event.last_seen_at,
            metadata=event.metadata,
        )
        return event

    def close_session(
        self, event_id: UUID, ended_at: datetime, duration_seconds: int
    ) -> Optional[DetectionEvent]:
        model = DetectionEventModel.objects.filter(id=event_id).first()
        if model is None:
            return None
        model.status = "CLOSED"
        model.ended_at = ended_at
        model.duration_seconds = duration_seconds
        model.save(update_fields=["status", "ended_at", "duration_seconds"])
        return self._to_entity(model)

    def attach_enrichment(
        self,
        event_id: UUID,
        clip_url: Optional[str],
        thumbnail_url: Optional[str],
        event_summary: Optional[str],
        extra_metadata: Optional[dict],
    ) -> Optional[DetectionEvent]:
        model = DetectionEventModel.objects.filter(id=event_id).first()
        if model is None:
            return None

        if clip_url is not None:
            model.clip_url = clip_url
        if thumbnail_url is not None:
            model.thumbnail_url = thumbnail_url
        if event_summary is not None:
            model.event_summary = event_summary
        if extra_metadata:
            model.metadata = {**model.metadata, **extra_metadata}

        model.is_enriched = True
        model.status = "ENRICHED"
        model.pipeline_stage = "ENRICHED"
        model.save(update_fields=[
            "clip_url", "thumbnail_url", "event_summary", "metadata",
            "is_enriched", "status", "pipeline_stage",
        ])
        return self._to_entity(model)

    def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        model = DetectionEventModel.objects.filter(id=event_id).first()
        return self._to_entity(model) if model else None

    def find_stale_open_sessions(self, older_than: datetime) -> list[DetectionEvent]:
        qs = DetectionEventModel.objects.filter(status="OPEN", last_seen_at__lt=older_than)
        return [self._to_entity(m) for m in qs]

    def count_recent_unknown(self, device_id, since: datetime) -> int:
        return DetectionEventModel.objects.filter(
            device_id=device_id, person_type="UNKNOWN", started_at__gte=since,
        ).count()

    def _to_entity(self, model) -> DetectionEvent:
        return DetectionEvent(
            id=model.id,
            home_id=model.home_id,
            device_id=model.device_id,
            track_id=model.track_id,
            status=model.status,
            pipeline_stage=model.pipeline_stage,
            event_type=model.event_type,
            person_type=model.person_type,
            person_label=model.person_label,
            member_id=model.matched_member_id,
            face_profile_id=model.matched_face_id,
            confidence_score=model.confidence_score,
            camera_location=model.camera_location,
            image_url=model.image_url,
            snapshot_url=model.snapshot_url,
            thumbnail_url=model.thumbnail_url,
            clip_url=model.clip_url,
            event_summary=model.event_summary,
            is_enriched=model.is_enriched,
            started_at=model.started_at,
            last_seen_at=model.last_seen_at,
            ended_at=model.ended_at,
            duration_seconds=model.duration_seconds,
            timestamp=model.timestamp,
            metadata=model.metadata,
        )
