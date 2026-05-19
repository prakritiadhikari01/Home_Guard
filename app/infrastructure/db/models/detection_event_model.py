import uuid
from django.db import models
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
    matched_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    confidence_score = models.FloatField(default=0.0)
    # In Phase 4 we may skip actual image storage; placeholder field if needed later
    image_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField()  # when the event occurred (from device)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "devices"  # use existing app label (devices or homes)
    
    def __str__(self):
        return f"Event {self.id} at {self.timestamp} in Home {self.home}"
