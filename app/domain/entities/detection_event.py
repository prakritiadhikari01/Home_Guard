from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class DetectionEvent:
    id: Optional[UUID]
    home_id: UUID
    device_id: UUID
    event_type: str
    person_type: str
    person_label: Optional[str]
    member_id: Optional[UUID]
    face_profile_id: Optional[UUID]
    confidence_score: float
    camera_location: Optional[str]
    image_url: Optional[str]
    snapshot_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    clip_url: Optional[str] = None
    event_summary: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: int = 0
    metadata: dict = field(default_factory=dict)
    is_enriched: bool = False
