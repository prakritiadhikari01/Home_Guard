from enum import Enum

_STAGE_ORDER = [
    "MOTION_DETECTED", "OBJECT_DETECTED", "TRACKING",
    "FACE_RECOGNIZED", "ENRICHMENT_QUEUED", "ENRICHED",
]

class PipelineStage(Enum):
    MOTION_DETECTED = "MOTION_DETECTED"
    OBJECT_DETECTED = "OBJECT_DETECTED"
    TRACKING = "TRACKING"
    FACE_RECOGNIZED = "FACE_RECOGNIZED"
    ENRICHMENT_QUEUED = "ENRICHMENT_QUEUED"
    ENRICHED = "ENRICHED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]

    @classmethod
    def rank(cls, value: str) -> int:
        """Used by the orchestrator to reject backward/out-of-order updates."""
        try:
            return _STAGE_ORDER.index(value)
        except ValueError:
            return -1


class EventStatus(Enum):
    OPEN = "OPEN"          # session actively being tracked
    CLOSED = "CLOSED"      # track lost / timed out, duration finalized
    ENRICHED = "ENRICHED"  # clip + summary attached, terminal state

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]