from django.db import models


class HomeSettings(models.Model):
    home = models.OneToOneField(
        "homes.Home",
        on_delete=models.CASCADE,
        related_name="settings",
    )

    # Household Notifications
    notify_family_members = models.BooleanField(default=False)
    emergency_contact_enabled = models.BooleanField(default=False)

    # Automation Rules
    notify_unknown_person = models.BooleanField(default=True)
    escalate_repeated_detection = models.BooleanField(default=True)
    log_known_member_entry = models.BooleanField(default=True)
    ignore_animals = models.BooleanField(default=False)

    # AI
    ai_summary_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "homes"
        
    def __str__(self):
        return f"{self.home.name} Settings"