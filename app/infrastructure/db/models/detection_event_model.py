import uuid

from django.db import models

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.domain.value_objects.person_type import PersonType
from app.domain.value_objects.event_type import EventType
class DetectionEvent(models.Model):
    """
    Stores all AI-generated events from cameras and sensors.
    This model is designed for future timeline queries such as:

    - Who appeared today?
    - Show unknown visitors this week.
    - When did Prakriti enter the living room?
    - Door unlock history.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="events"
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="events"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices(),
        default=EventType.PERSON_DETECTED.value,
    )
    
    person_type = models.CharField(
        max_length=20,
        choices=PersonType.choices(),
        default=PersonType.UNKNOWN.value,
    )

    person_label = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    matched_member = models.ForeignKey(
        HomeMember,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="detection_events"
    )

    matched_face = models.ForeignKey(
        FaceProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events"
    )

    confidence_score = models.FloatField(
        default=0.0
    )

    camera_location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    thumbnail_url = models.URLField(
        blank=True,
        null=True
    )
    image_url = models.URLField(
        null=True,
        blank=True
    )

    snapshot_url = models.TextField(
        null=True,
        blank=True
    )

    event_summary = models.TextField(
        null=True,
        blank=True
    )

    duration_seconds = models.PositiveIntegerField(
        default=0
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    timestamp = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        app_label = "events"

        ordering = [
            "-timestamp"
        ]

        indexes = [
            models.Index(
                fields=["timestamp"]
            ),
            models.Index(
                fields=["person_type"]
            ),
            models.Index(
                fields=["event_type"]
            ),
            models.Index(
                fields=["camera_location"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.event_type} | "
            f"{self.person_type} | "
            f"{self.timestamp}"
        )