from django.db import models


class DeviceSettings(models.Model):
    device = models.OneToOneField(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="settings",
    )

    # Detection
    human_detection = models.BooleanField(default=True)
    animal_detection = models.BooleanField(default=True)
    vehicle_detection = models.BooleanField(default=True)
    motion_detection = models.BooleanField(default=True)

    # AI
    confidence_threshold = models.PositiveSmallIntegerField(default=80)

    # Recording
    recording_enabled = models.BooleanField(default=True)

    # Device
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "devices"
        constraints = [
            models.CheckConstraint(
                check=models.Q(confidence_threshold__gte=0)
                & models.Q(confidence_threshold__lte=100),
                name="device_confidence_threshold_valid",
            )
        ]

    def __str__(self):
        return f"{self.device.name} Settings"