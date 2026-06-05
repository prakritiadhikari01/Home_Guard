#app/domain/value_objects/device_status.py
from enum import Enum


class DeviceStatus(Enum):

    ONLINE = "online"
    OFFLINE = "offline"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]