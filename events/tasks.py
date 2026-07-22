# app/tasks.py
"""
Celery beat task: closes any DetectionEvent stuck in OPEN status because the
AI engine crashed / lost network before sending an explicit close. Schedule
this to run every ~30-60s in your Celery beat config, e.g.:

CELERY_BEAT_SCHEDULE = {
    "sweep-stale-detection-sessions": {
        "task": "app.tasks.sweep_stale_sessions",
        "schedule": 30.0,
    },
}
"""
from celery import shared_task

from app.domain.services.event_orchestrator import EventOrchestrator
from app.infrastructure.db.repositories.django_detection_event_repository import (
    DjangoDetectionEventRepository,
)
from app.infrastructure.db.repositories.django_alert_repository import DjangoAlertRepository


@shared_task
def sweep_stale_sessions():
    repository = DjangoDetectionEventRepository()
    alert_repository = DjangoAlertRepository()
    orchestrator = EventOrchestrator(repository, alert_repository)
    closed_count = orchestrator.sweep_stale_sessions()
    return {"closed": closed_count}
