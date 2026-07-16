from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from app.interfaces.api.permissions.service_permissions import IsAIEngine
from app.interfaces.api.serializers.event_serializers import (
    EventIngestSerializer,
    DetectionEventResponseSerializer,
)
from app.application.services.detection_event_service import DetectionEventService
from app.domain.services.event_orchestrator import EventOrchestrator
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
    return DetectionEventService(orchestrator)


class EventIngestView(APIView):
    """
    POST /api/events/ingest/

    Called by the FastAPI AI engine (Windows) on every processed frame
    that produces a detection. Handles dedup/merge via the orchestrator,
    so this endpoint is safe to hammer at frame rate.
    """

    # TODO: replace with whatever scheme your enrollment endpoints use
    # (shared API key / service token), not open AllowAny long-term.
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

        response_data = {
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
            "timestamp": detection_event.timestamp,
            "duration_seconds": detection_event.duration_seconds,
            "metadata": detection_event.metadata,
        }
        response_serializer = DetectionEventResponseSerializer(response_data)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)