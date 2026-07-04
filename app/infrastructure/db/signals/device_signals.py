from django.db.models.signals import post_save
from django.dispatch import receiver

from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.device_settings_model import DeviceSettings


@receiver(post_save, sender=Device)
def create_device_settings(sender, instance, created, **kwargs):
    if created:
        DeviceSettings.objects.create(
            device=instance
        )