import uuid

from django.db import models

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.face_profile_model import FaceProfile


class DetectionEvent(models.Model):
    """
    Stores all AI-generated events from cameras and sensors.
    This model is designed for future timeline queries such as:

    - Who appeared today?
    - Show unknown visitors this week.
    - When did Prakriti enter the living room?
    - Door unlock history.
    """

    PERSON_TYPE_CHOICES = [
        ("KNOWN", "Known Person"),
        ("UNKNOWN", "Unknown Person"),
        ("INTRUDER", "Intruder"),
        ("VEHICLE", "Vehicle"),
    ]

    EVENT_TYPE_CHOICES = [
        ("PERSON_DETECTED", "Person Detected"),
        ("DOOR_UNLOCKED", "Door Unlocked"),
        ("DOOR_LOCKED", "Door Locked"),
        ("MOTION_DETECTED", "Motion Detected"),
        ("VEHICLE_DETECTED", "Vehicle Detected"),
    ]

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
        choices=EVENT_TYPE_CHOICES,
        default="PERSON_DETECTED"
    )

    person_type = models.CharField(
        max_length=20,
        choices=PERSON_TYPE_CHOICES,
        default="UNKNOWN"
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