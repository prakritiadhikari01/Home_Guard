from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Alert:
    id: Optional[UUID]
    home_id: UUID
    event_id: UUID

    severity: str
    reason: str
    status: str = "ACTIVE"

    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
