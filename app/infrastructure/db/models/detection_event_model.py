import uuid

from django.db import models

from app.domain.value_objects.events import EventStatus, PipelineStage
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.domain.value_objects.person_type import PersonType
from app.domain.value_objects.event_type import EventType


class DetectionEvent(models.Model):
    """
    One row per tracked-entity session (one ByteTrack track_id on one
    device). Created the instant motion/tracking assigns an identity, then
    PATCHED repeatedly as the pipeline progresses. See
    docs/detection-event-architecture.md for the full state machine and
    business rules — this model is a direct implementation of that doc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="events")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="events")

    track_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="ByteTrack track id. Unique only among currently-OPEN sessions per device.",
    )

    status = models.CharField(
        max_length=20, choices=EventStatus.choices(), default=EventStatus.OPEN.value,
    )
    pipeline_stage = models.CharField(
        max_length=30, choices=PipelineStage.choices(), default=PipelineStage.MOTION_DETECTED.value,
    )

    event_type = models.CharField(
        max_length=50, choices=EventType.choices(), default=EventType.MOTION_DETECTED.value,
    )
    person_type = models.CharField(
        max_length=20, choices=PersonType.choices(), default=PersonType.UNKNOWN.value,
    )
    person_label = models.CharField(max_length=255, null=True, blank=True)

    matched_member = models.ForeignKey(
        HomeMember, null=True, blank=True, on_delete=models.SET_NULL, related_name="detection_events",
    )
    matched_face = models.ForeignKey(
        FaceProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="events",
    )

    confidence_score = models.FloatField(default=0.0)
    camera_location = models.CharField(max_length=255, null=True, blank=True)

    thumbnail_url = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    snapshot_url = models.TextField(null=True, blank=True)
    clip_url = models.URLField(null=True, blank=True)
    event_summary = models.TextField(null=True, blank=True)
    is_enriched = models.BooleanField(default=False)

    started_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    # Kept for backward compatibility with existing queries; mirrors
    # started_at, set once at creation, never mutated afterward.
    timestamp = models.DateTimeField()

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["person_type"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["camera_location"]),
            models.Index(fields=["device", "track_id", "status"], name="idx_track_session_lookup"),
        ]

    def __str__(self):
        return f"{self.event_type} | {self.person_type} | {self.status} | {self.timestamp}"
