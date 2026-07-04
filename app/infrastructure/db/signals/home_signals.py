from django.db.models.signals import post_save
from django.dispatch import receiver

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.home_settings_model import HomeSettings


@receiver(post_save, sender=Home)
def create_home_settings(sender, instance, created, **kwargs):
    if created:
        HomeSettings.objects.create(
            home=instance
        )