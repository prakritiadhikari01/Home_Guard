from enum import Enum


class AlertStatus(Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class AlertReason(Enum):
    INTRUDER_DETECTED = "INTRUDER_DETECTED"
    UNKNOWN_PERSON = "UNKNOWN_PERSON"
    REPEATED_UNKNOWN = "REPEATED_UNKNOWN"
    LOITERING = "LOITERING"
    UNRECOGNIZED_VEHICLE = "UNRECOGNIZED_VEHICLE"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]

from enum import Enum


class AlertSeverity(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]
