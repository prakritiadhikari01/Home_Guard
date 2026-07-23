from django.db.models.signals import post_save
from django.dispatch import receiver

from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.device_settings_model import DeviceSettings

from app.domain.value_objects.device_type import DeviceType


@receiver(post_save, sender=Device)
def create_device_settings(sender, instance, created, **kwargs):
    if created:
        DeviceSettings.objects.create(
            device=instance
        )

@receiver(post_save, sender=Device)
def auto_pair_smart_lock_to_camera(sender, instance: Device, created, **kwargs):
    """
    When a smart lock device is saved and doesn't already have a
    paired_camera, look for a camera in the same home with a matching
    stream_url and link them. Registration itself is untouched — this
    just fills in the relationship implicitly after the fact.
    """
    if instance.device_type != DeviceType.SMART_LOCK.value:
        return

    if instance.paired_camera_id is not None:
        return

    if not instance.stream_url:
        return

    matching_camera = (
        Device.objects.filter(
            home=instance.home,
            device_type=DeviceType.CAMERA.value,
            stream_url=instance.stream_url,
        )
        .exclude(id=instance.id)
        .first()
    )

    if matching_camera:
        Device.objects.filter(id=instance.id).update(paired_camera=matching_camera)
        print(f"[device_signals] Auto-paired lock {instance.id} ({instance.name}) -> camera {matching_camera.id} ({matching_camera.name})")
    else:
        print(f"[device_signals] No matching camera found for lock {instance.id} ({instance.name}) with stream_url={instance.stream_url}")