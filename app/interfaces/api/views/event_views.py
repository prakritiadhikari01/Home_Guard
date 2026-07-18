from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.interfaces.api.permissions.service_permissions import IsAIEngine
from app.interfaces.api.serializers.event_serializers import (
    EventIngestSerializer,
    EventEnrichSerializer,
    DetectionEventResponseSerializer,
)
from app.application.services.detection_event_service import DetectionEventService
from app.domain.services.event_orchestrator import EventOrchestrator
from app.domain.entities.detection_event import DetectionEvent
from app.infrastructure.db.repositories.django_detection_event_repository import (
    DjangoDetectionEventRepository,
)


def get_detection_event_service() -> DetectionEventService:
    """
    Simple manual composition root — swap this for a DI container later
    if the app grows. Kept here so the view doesn't know about
    concrete infrastructure classes.
    """
    repository = DjangoDetectionEventRepository()
    orchestrator = EventOrchestrator(repository)
    return DetectionEventService(orchestrator, repository)


def _serialize_event(detection_event: DetectionEvent) -> dict:
    return {
        "id": detection_event.id,
        "home_id": detection_event.home_id,
        "device_id": detection_event.device_id,
        "event_type": detection_event.event_type,
        "person_type": detection_event.person_type,
        "person_label": detection_event.person_label,
        "confidence_score": detection_event.confidence_score,
        "camera_location": detection_event.camera_location,
        "image_url": detection_event.image_url,
        "snapshot_url": detection_event.snapshot_url,
        "thumbnail_url": detection_event.thumbnail_url,
        "clip_url": detection_event.clip_url,
        "event_summary": detection_event.event_summary,
        "is_enriched": detection_event.is_enriched,
        "timestamp": detection_event.timestamp,
        "duration_seconds": detection_event.duration_seconds,
        "metadata": detection_event.metadata,
    }


class EventIngestView(APIView):
    """
    POST /api/events/ingest/

    Called by the FastAPI AI engine (Windows) the instant a detection happens.
    Handles dedup/merge via the orchestrator, so this endpoint is safe to hammer
    at frame rate. Does NOT wait on clip generation or VLM summaries — those are
    attached later via EventEnrichView.
    """

    permission_classes = [IsAIEngine]

    def post(self, request):
        serializer = EventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()

        try:
            detection_event = service.ingest(serializer.validated_data)
        except Exception as exc:
            return Response(
                {"error": f"Failed to process detection event: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = DetectionEventResponseSerializer(_serialize_event(detection_event))
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class EventEnrichView(APIView):
    """
    PATCH /api/events/<uuid:event_id>/enrich/

    Called by the AI engine once it has finished the slower VLM pass on the
    clip for this event — attaches clip_url, thumbnail_url, event_summary,
    and any extra structured attributes. Safe to call once the event already
    exists; 404s if the event_id is unknown (e.g. it was never ingested).
    """

    permission_classes = [IsAIEngine]

    def patch(self, request, event_id):
        serializer = EventEnrichSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()

        try:
            detection_event = service.enrich(event_id, serializer.validated_data)
        except Exception as exc:
            return Response(
                {"error": f"Failed to enrich detection event: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if detection_event is None:
            return Response(
                {"error": f"No event found with id {event_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = DetectionEventResponseSerializer(_serialize_event(detection_event))
        return Response(response_serializer.data, status=status.HTTP_200_OK)
