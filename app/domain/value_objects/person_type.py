from enum import Enum


class PersonType(Enum):

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    INTRUDER = "INTRUDER"
    VEHICLE = "VEHICLE"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]