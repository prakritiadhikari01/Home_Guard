from enum import Enum


class LockStatus(Enum):

    LOCKED = "locked"
    UNLOCKED = "unlocked"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]