from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class DetectionEvent:
    """
    Domain entity for one tracked-entity session. Mirrors the Django model
    but stays framework-free. `id=None` on construction means "not yet
    persisted" — the repository's create()/open_session() assigns one.
    """

    id: Optional[UUID]
    home_id: UUID
    device_id: UUID
    track_id: str

    status: str
    pipeline_stage: str

    event_type: str
    person_type: str
    person_label: Optional[str] = None
    member_id: Optional[UUID] = None
    face_profile_id: Optional[UUID] = None
    confidence_score: float = 0.0

    camera_location: Optional[str] = None

    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    snapshot_url: Optional[str] = None
    clip_url: Optional[str] = None
    event_summary: Optional[str] = None
    is_enriched: bool = False

    started_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0

    timestamp: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def is_open(self) -> bool:
        return self.status == "OPEN"

    def is_closed(self) -> bool:
        return self.status in ("CLOSED", "ENRICHED")
