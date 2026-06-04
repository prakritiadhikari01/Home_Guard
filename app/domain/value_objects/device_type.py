#app/domain/value_objects/device_type.py
from enum import Enum


class DeviceType(Enum):

    CAMERA = "camera"
    SMART_LOCK = "smart_lock"
    SENSOR = "sensor"
    ALARM = "alarm"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]