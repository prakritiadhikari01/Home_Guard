from django.db.models.signals import post_save
from django.dispatch import receiver

from app.infrastructure.db.models.user_settings_model import UserSettings
from accounts.models import User


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(
            user=instance
        )