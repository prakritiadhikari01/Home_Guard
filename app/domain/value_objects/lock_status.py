from enum import Enum


class LockStatus(Enum):

    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    VERIFYING = "VERIFYING"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]