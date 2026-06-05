#app/infrastructure/db/models/detection_event_model.py
import uuid
from django.db import models
from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from django.conf import settings

class DetectionEvent(models.Model):
    """
    Stores each camera/sensor event and AI results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="events")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="events")
    # PersonType: KNOWN or UNKNOWN
    PERSON_TYPE_CHOICES = [
        ("KNOWN", "Known Person"),
        ("UNKNOWN", "Unknown Person"),
        ("INTRUDER", "Intruder"),
        ("VEHICLE", "Vehicle"),
    ]
    person_type = models.CharField(max_length=20, choices=PERSON_TYPE_CHOICES, default="UNKNOWN")
    # If recognized, link to User (optional, since face profiles not set up yet)
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
    snapshot_url = models.TextField(
        null=True,
        blank=True
    )
    event_type = models.CharField(
        max_length=50,
        default="PERSON_DETECTED"
    )

    event_summary = models.TextField(
        blank=True,
        null=True
    )

    person_label = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    duration_seconds = models.IntegerField(
        default=0
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )
    camera_location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    confidence_score = models.FloatField(default=0.0)
    # In Phase 4 we may skip actual image storage; placeholder field if needed later
    image_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField()  # when the event occurred (from device)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "events"  # use existing app label (devices or homes)
    
    def __str__(self):
        return f"{self.person_type} | {self.home.name} | {self.timestamp}"
