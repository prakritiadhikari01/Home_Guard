# app/domain/repositories/device_repository.py
from abc import ABC, abstractmethod


class AbstractDeviceRepository(ABC):

    @abstractmethod
    def create_device(self, home, **kwargs):
        ...

    @abstractmethod
    def get_home_devices(self, home):
        ...

    @abstractmethod
    def get_device_by_id(self, device_id):
        ...

    @abstractmethod
    def update_device(self, device, data):
        ...

    @abstractmethod
    def delete_device(self, device):
        ...