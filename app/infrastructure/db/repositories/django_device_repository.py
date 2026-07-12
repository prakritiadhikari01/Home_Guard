# app/infrastructure/db/repositories/django_device_repository.py
# app/infrastructure/db/repositories/django_device_repository.py
from app.domain.repositories.device_repository import AbstractDeviceRepository
from app.infrastructure.db.models.device_model import Device


class DjangoDeviceRepository(AbstractDeviceRepository):

    def create_device(self, home, **kwargs):
        return Device.objects.create(home=home, **kwargs)

    def get_home_devices(self, home):
        return Device.objects.filter(home=home).order_by("-created_at")

    def get_device_by_id(self, device_id):
        return Device.objects.select_related("home").filter(id=device_id).first()

    def update_device(self, device, data):
        for field, value in data.items():
            setattr(device, field, value)
        device.save()
        return device

    def delete_device(self, device):
        device.delete()