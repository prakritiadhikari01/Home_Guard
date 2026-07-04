from enum import Enum


class EventType(Enum):

    PERSON_DETECTED = "PERSON_DETECTED"
    DOOR_UNLOCKED = "DOOR_UNLOCKED"
    DOOR_LOCKED = "DOOR_LOCKED"
    MOTION_DETECTED = "MOTION_DETECTED"
    VEHICLE_DETECTED = "VEHICLE_DETECTED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]