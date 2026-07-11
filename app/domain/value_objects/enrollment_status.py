from enum import Enum


class EnrollmentStatus(Enum):

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    @classmethod
    def choices(cls):
        return [(status.value, status.value) for status in cls]