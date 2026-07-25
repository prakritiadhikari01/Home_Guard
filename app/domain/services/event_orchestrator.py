from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.domain.entities.alerts import Alert
from app.domain.entities.detection_event import DetectionEvent
from app.domain.repositories.detection_event_repository import DetectionEventRepository
from app.domain.repositories.alert_repository import AlertRepository
from app.domain.value_objects.events import PipelineStage

STALE_SESSION_TIMEOUT_SECONDS = 30
LOITERING_THRESHOLD_SECONDS = 600
REPEATED_UNKNOWN_WINDOW_MINUTES = 15
REPEATED_UNKNOWN_COUNT = 3


class EventOrchestrator:
    """
    Owns the session state machine (open → progress → close → enrich) and
    alert-decision logic. Views/services call this; it never talks to Django
    directly — everything goes through the repository interfaces so it stays
    testable without a DB.
    """

    def __init__(self, repository: DetectionEventRepository, alert_repository: AlertRepository):
        self.repository = repository
        self.alert_repository = alert_repository

    # ---- fast path: motion/tracking assigns a track_id ----
    def open_session(self, incoming: DetectionEvent) -> DetectionEvent:
        # Idempotency: a duplicate "open" for a track that's already OPEN is
        # treated as a progress update, not an error/new row.
        existing = self.repository.find_open_by_track(incoming.device_id, incoming.track_id)
        if existing:
            return self.update_progress(existing.id, incoming)
        return self.repository.create(incoming)

    # ---- called repeatedly as object/face recognition resolve ----
    def update_progress(self, event_id: UUID, incoming: DetectionEvent) -> Optional[DetectionEvent]:
        current = self.repository.get_by_id(event_id)
        if current is None:
            return None

        # A patch arriving for an already-closed session is stale/duplicate —
        # no-op rather than mutate a finished record.
        if current.is_closed():
            return current

        current.confidence_score = max(current.confidence_score, incoming.confidence_score)

        # person_type upgrade only: UNKNOWN -> KNOWN/INTRUDER, never downgrade.
        if current.person_type == "UNKNOWN" and incoming.person_type != "UNKNOWN":
            current.person_type = incoming.person_type
        elif current.person_type == incoming.person_type:
            pass  # no change
        # else: keep current classification, ignore a lower-confidence conflicting read

        if incoming.member_id and not current.member_id:
            current.member_id = incoming.member_id
        if incoming.face_profile_id and not current.face_profile_id:
            current.face_profile_id = incoming.face_profile_id
        if incoming.person_label and not current.person_label:
            current.person_label = incoming.person_label

        # event_type upgrade: generic -> specific, but don't silently flip
        # between unrelated types (that indicates two tracks got merged).
        if current.event_type == "MOTION_DETECTED" and incoming.event_type != "MOTION_DETECTED":
            current.event_type = incoming.event_type

        if not current.thumbnail_url and incoming.thumbnail_url:
            current.thumbnail_url = incoming.thumbnail_url
        if incoming.image_url:
            current.image_url = incoming.image_url
        if incoming.snapshot_url:
            current.snapshot_url = incoming.snapshot_url

        # pipeline_stage only moves forward
        if PipelineStage.rank(incoming.pipeline_stage) > PipelineStage.rank(current.pipeline_stage):
            current.pipeline_stage = incoming.pipeline_stage

        current.last_seen_at = incoming.last_seen_at or datetime.utcnow()
        current.metadata = {**current.metadata, **(incoming.metadata or {})}

        return self.repository.update_progress(current)

    # ---- track lost / explicit close ----
    def close_session(self, event_id: UUID, ended_at: datetime) -> Optional[DetectionEvent]:
        current = self.repository.get_by_id(event_id)
        if current is None or current.is_closed():
            return current

        duration = int((ended_at - current.started_at).total_seconds()) if current.started_at else 0
        closed = self.repository.close_session(event_id, ended_at, max(duration, 0))
        if closed:
            self._evaluate_alerts(closed)
        return closed

    # ---- safety net for sessions the AI engine never explicitly closed ----
    def sweep_stale_sessions(self) -> int:
        cutoff = datetime.utcnow() - timedelta(seconds=STALE_SESSION_TIMEOUT_SECONDS)
        stale = self.repository.find_stale_open_sessions(cutoff)
        for event in stale:
            event.metadata = {**event.metadata, "closed_reason": "timeout"}
            self.close_session(event.id, event.last_seen_at)
        return len(stale)

    # ---- Celery enrichment worker ----
    def attach_enrichment(
        self,
        event_id: UUID,
        clip_url: Optional[str],
        thumbnail_url: Optional[str],
        event_summary: Optional[str],
        extra_metadata: Optional[dict],
    ) -> Optional[DetectionEvent]:
        return self.repository.attach_enrichment(
            event_id, clip_url, thumbnail_url, event_summary, extra_metadata
        )

    # ---- alert decision, run at close-time ----
    def _evaluate_alerts(self, event: DetectionEvent) -> None:
        if event.person_type == "INTRUDER":
            self._raise_alert(event, "INTRUDER_DETECTED", "CRITICAL")

        if event.person_type == "UNKNOWN":
            since = datetime.utcnow() - timedelta(minutes=REPEATED_UNKNOWN_WINDOW_MINUTES)
            recent_unknown_count = self.repository.count_recent_unknown(event.device_id, since)
            if recent_unknown_count >= REPEATED_UNKNOWN_COUNT:
                self._raise_alert(event, "REPEATED_UNKNOWN", "CRITICAL")

        if event.duration_seconds >= LOITERING_THRESHOLD_SECONDS and event.person_type != "KNOWN":
            self._raise_alert(event, "LOITERING", "WARNING")

        if event.event_type == "VEHICLE_DETECTED" and event.person_type != "KNOWN":
            self._raise_alert(event, "UNRECOGNIZED_VEHICLE", "WARNING")

    def _raise_alert(self, event: DetectionEvent, reason: str, severity: str) -> Alert:
        alert = Alert(
            id=None,
            home_id=event.home_id,
            event_id=event.id,
            severity=severity,
            reason=reason,
        )
        return self.alert_repository.create_if_not_exists(alert)
