#app/infrastructure/db/repositories/django_detection_event_repository.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.repositories.detection_event_repository import DetectionEventRepository
from app.domain.entities.detection_event import DetectionEvent
from app.infrastructure.db.models.detection_event_model import DetectionEvent as DetectionEventModel


class DjangoDetectionEventRepository(DetectionEventRepository):

    def find_recent_open_event(
        self, device_id, person_type: str, face_profile_id, since: datetime
    ) -> Optional[DetectionEvent]:
        qs = DetectionEventModel.objects.filter(
            device_id=device_id,
            person_type=person_type,
            timestamp__gte=since,
        )
        # None == None matches everything in Django's ORM for FK filters,
        # so unknown visitors (face_profile_id=None) still bucket together correctly.
        qs = qs.filter(matched_face_id=face_profile_id)

        model = qs.order_by("-timestamp").first()
        return self._to_entity(model) if model else None

    def create(self, event: DetectionEvent) -> DetectionEvent:
        model = DetectionEventModel.objects.create(
            home_id=event.home_id,
            device_id=event.device_id,
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
            clip_url=event.clip_url,
            event_summary=event.event_summary,
            is_enriched=event.is_enriched,
            timestamp=event.timestamp,
            duration_seconds=event.duration_seconds,
            metadata=event.metadata,
        )
        return self._to_entity(model)

    def update(self, event: DetectionEvent) -> DetectionEvent:
        # Deliberately does NOT touch clip_url / event_summary / is_enriched —
        # those are owned by update_enrichment() and must survive a merge untouched.
        DetectionEventModel.objects.filter(id=event.id).update(
            timestamp=event.timestamp,
            duration_seconds=event.duration_seconds,
            confidence_score=event.confidence_score,
            image_url=event.image_url,
            snapshot_url=event.snapshot_url,
            thumbnail_url=event.thumbnail_url,
            metadata=event.metadata,
        )
        return event

    def get_by_id(self, event_id: UUID) -> Optional[DetectionEvent]:
        model = DetectionEventModel.objects.filter(id=event_id).first()
        return self._to_entity(model) if model else None

    def update_enrichment(
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
            # Merge rather than replace — keep occurrence_count etc. set by the orchestrator.
            model.metadata = {**model.metadata, **extra_metadata}

        model.is_enriched = True
        model.save(update_fields=[
            "clip_url", "thumbnail_url", "event_summary", "metadata", "is_enriched",
        ])
        return self._to_entity(model)

    def _to_entity(self, model) -> DetectionEvent:
        return DetectionEvent(
            id=model.id,
            home_id=model.home_id,
            device_id=model.device_id,
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
            timestamp=model.timestamp,
            duration_seconds=model.duration_seconds,
            metadata=model.metadata,
        )
