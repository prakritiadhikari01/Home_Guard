# app/infrastructure/db/repositories/django_device_repository.py
from app.infrastructure.db.models.device_model import Device


class DjangoDeviceRepository:

    @staticmethod
    def create_device(**kwargs):
        return Device.objects.create(**kwargs)

    @staticmethod
    def get_home_devices(home):
        return Device.objects.filter(home=home)

    @staticmethod
    def get_device_by_id(device_id):
        return Device.objects.filter(
            id=device_id
        ).first()