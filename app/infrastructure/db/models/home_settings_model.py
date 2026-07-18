from django.db import models


class HomeSettings(models.Model):
    home = models.OneToOneField(
        "homes.Home",
        on_delete=models.CASCADE,
        related_name="settings",
    )

    # Timeline

    timeline_enabled = models.BooleanField(default=True)
    log_known_member_entry = models.BooleanField(default=True)
    log_unknown_person = models.BooleanField(default=True)

    # Alerts

    notify_unknown_person = models.BooleanField(default=True)
    notify_family_members = models.BooleanField(default=False)
    emergency_contact_enabled = models.BooleanField(default=False)
    escalate_repeated_detection = models.BooleanField(default=True)

    # AI

    ai_summary_enabled = models.BooleanField(default=True)

    # Recording

    clip_recording_enabled = models.BooleanField(default=True)
    snapshot_enabled = models.BooleanField(default=True)

    # Detection Rules

    ignore_animals = models.BooleanField(default=False)
    loitering_seconds = models.PositiveIntegerField(
        default=20,
    )
    repeated_detection_window = models.PositiveIntegerField(
        default=300,
        help_text="Seconds before repeated detections are considered a new occurrence.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        app_label = "homes"

    def __str__(self):
        return f"{self.home.name} Settings"