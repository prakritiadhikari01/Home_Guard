from enum import Enum


class SecurityMode(Enum):
    NORMAL = "NORMAL"
    AWAY = "AWAY"
    HIGH = "HIGH"
    SOS = "SOS"

    @classmethod
    def choices(cls):
        return [(mode.value, mode.name.replace("_", " ").title()) for mode in cls]