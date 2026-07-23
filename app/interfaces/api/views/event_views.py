from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from app.infrastructure.db.models.alerts_model import Alert
from app.interfaces.api.permissions.service_permissions import IsAIEngine

from app.application.services.detection_event_service import DetectionEventService
from app.domain.services.event_orchestrator import EventOrchestrator
from app.domain.entities.detection_event import DetectionEvent
from app.infrastructure.db.repositories.django_detection_event_repository import (
    DjangoDetectionEventRepository,
)
from app.infrastructure.db.repositories.django_alert_repository import DjangoAlertRepository
from app.infrastructure.db.models.detection_event_model import DetectionEvent as DetectionEventModel
from app.interfaces.api.serializers.event_serializer import AlertSerializer, DetectionEventListSerializer, DetectionEventResponseSerializer, EventCloseSerializer, EventEnrichSerializer, EventOpenSerializer, EventProgressSerializer


def get_detection_event_service() -> DetectionEventService:
    """Manual composition root — swap for a DI container later if the app grows."""
    repository = DjangoDetectionEventRepository()
    alert_repository = DjangoAlertRepository()
    orchestrator = EventOrchestrator(repository, alert_repository)
    return DetectionEventService(orchestrator, repository)


def _serialize_event(detection_event: DetectionEvent) -> dict:
    return {
        "id": detection_event.id,
        "home_id": detection_event.home_id,
        "device_id": detection_event.device_id,
        "track_id": detection_event.track_id,
        "status": detection_event.status,
        "pipeline_stage": detection_event.pipeline_stage,
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
        "started_at": detection_event.started_at,
        "last_seen_at": detection_event.last_seen_at,
        "ended_at": detection_event.ended_at,
        "duration_seconds": detection_event.duration_seconds,
        "timestamp": detection_event.timestamp,
        "metadata": detection_event.metadata,
    }


class EventOpenView(APIView):
    """
    POST /api/events/open/

    Called the instant motion + tracking assigns a track_id. Fast path —
    safe to hammer at frame rate, idempotent if the track is already OPEN.
    """
    permission_classes = [IsAIEngine]

    def post(self, request):
        serializer = EventOpenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()
        try:
            event = service.open(serializer.validated_data)
        except Exception as exc:
            return Response({"error": f"Failed to open session: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DetectionEventResponseSerializer(_serialize_event(event)).data,
            status=status.HTTP_201_CREATED,
        )


class EventProgressView(APIView):
    """
    PATCH /api/events/<uuid:event_id>/progress/

    Called repeatedly as object/face recognition resolve more detail about
    an already-open session. No-op if the session is already closed
    (protects against stale/out-of-order requests from the AI engine).
    """
    permission_classes = [IsAIEngine]

    def patch(self, request, event_id):
        serializer = EventProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()
        try:
            event = service.progress(event_id, serializer.validated_data)
        except Exception as exc:
            return Response({"error": f"Failed to update session: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        if event is None:
            return Response({"error": f"No event found with id {event_id}"}, status=status.HTTP_404_NOT_FOUND)

        return Response(DetectionEventResponseSerializer(_serialize_event(event)).data)


class EventCloseView(APIView):
    """
    PATCH /api/events/<uuid:event_id>/close/

    Called when ByteTrack loses the track. Finalizes duration and triggers
    alert evaluation. A Celery beat sweep also calls this path for sessions
    the AI engine never explicitly closed (crash / network drop).
    """
    permission_classes = [IsAIEngine]

    def patch(self, request, event_id):
        serializer = EventCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()
        event = service.close(event_id, serializer.validated_data)

        if event is None:
            return Response({"error": f"No event found with id {event_id}"}, status=status.HTTP_404_NOT_FOUND)

        return Response(DetectionEventResponseSerializer(_serialize_event(event)).data)


class EventEnrichView(APIView):
    """
    PATCH /api/events/<uuid:event_id>/enrich/

    Called by the Celery summary worker once clip/VLM pass is done. Only
    valid on a CLOSED session. Unchanged contract from before.
    """
    permission_classes = [IsAIEngine]

    def patch(self, request, event_id):
        serializer = EventEnrichSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_detection_event_service()
        try:
            event = service.enrich(event_id, serializer.validated_data)
        except Exception as exc:
            return Response({"error": f"Failed to enrich event: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        if event is None:
            return Response({"error": f"No event found with id {event_id}"}, status=status.HTTP_404_NOT_FOUND)

        return Response(DetectionEventResponseSerializer(_serialize_event(event)).data)


class HomeEventListView(ListAPIView):
    """
    GET /api/homes/<uuid:home_id>/events/?category=recognized&limit=100

    Read-only listing for Timeline page. Pure read path (no dedup, no state
    transitions) so it queries the Django model directly.
    """
    serializer_class = DetectionEventListSerializer
    permission_classes = [IsAuthenticated]

    CATEGORY_FILTERS = {
        "recognized": {"person_type": "KNOWN"},
        "unknown": {"person_type": "UNKNOWN"},
        "alerts": {"person_type": "INTRUDER"},
        "doors": {"event_type__in": ["DOOR_LOCKED", "DOOR_UNLOCKED"]},
        "vehicles": {"event_type": "VEHICLE_DETECTED"},
        "animals": {"event_type": "MOTION_DETECTED"},
    }

    def get_queryset(self):
        qs = DetectionEventModel.objects.filter(
            home_id=self.kwargs["home_id"]
        ).select_related("matched_member", "device").order_by("-timestamp")

        category = self.request.query_params.get("category")
        if category and category != "all":
            qs = qs.filter(**self.CATEGORY_FILTERS.get(category, {}))

        limit = int(self.request.query_params.get("limit", 100))
        return qs[:limit]


class HomeAlertListView(ListAPIView):
    """GET /api/homes/<uuid:home_id>/alerts/?status=active"""
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Alert.objects.filter(home_id=self.kwargs["home_id"])
        status_filter = self.request.query_params.get("status", "ACTIVE").upper()
        qs = qs.filter(status=status_filter)
        return qs.select_related("event").order_by("-created_at")


class AlertResolveView(APIView):
    """PATCH /api/alerts/<uuid:alert_id>/resolve/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, alert_id):
        repo = DjangoAlertRepository()
        alert = repo.resolve(alert_id, request.user.id)
        if alert is None:
            return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(AlertSerializer(alert.__dict__).data)


class AlertDismissView(APIView):
    """PATCH /api/alerts/<uuid:alert_id>/dismiss/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, alert_id):
        repo = DjangoAlertRepository()
        alert = repo.dismiss(alert_id)
        if alert is None:
            return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(AlertSerializer(alert.__dict__).data)


# Add to app/interfaces/api/views/event_views.py

from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser
from app.infrastructure.db.models.detection_event_model import DetectionEvent as DetectionEventModel


class EventClipUploadView(APIView):
    """
    PATCH /api/events/<uuid:event_id>/upload-clip/   (multipart, field name "clip")

    Engine uploads the actual clip file bytes here — Django stores it in
    its own media storage and becomes the source of truth for clip_url.
    This replaces relying on the Windows engine machine staying online/
    reachable forever just to serve a file it hosts locally; Django is
    the persistent backend, so it should own the durable copy.
    """
    permission_classes = [IsAIEngine]
    parser_classes = [MultiPartParser]

    def patch(self, request, event_id):
        event = DetectionEventModel.objects.filter(id=event_id).first()
        if event is None:
            return Response({"error": f"No event found with id {event_id}"}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("clip")
        if not file:
            return Response({"error": "No 'clip' file provided"}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f"clips/{event_id}.mp4", file)
        url = request.build_absolute_uri(default_storage.url(path))

        event.clip_url = url
        event.save(update_fields=["clip_url"])
        return Response({"clip_url": url}, status=status.HTTP_200_OK)


class EventThumbnailUploadView(APIView):
    """PATCH /api/events/<uuid:event_id>/upload-thumbnail/   (multipart, field name "thumbnail")"""
    permission_classes = [IsAIEngine]
    parser_classes = [MultiPartParser]

    def patch(self, request, event_id):
        event = DetectionEventModel.objects.filter(id=event_id).first()
        if event is None:
            return Response({"error": f"No event found with id {event_id}"}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("thumbnail")
        if not file:
            return Response({"error": "No 'thumbnail' file provided"}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f"thumbnails/{event_id}.jpg", file)
        url = request.build_absolute_uri(default_storage.url(path))

        event.thumbnail_url = url
        event.save(update_fields=["thumbnail_url"])
        return Response({"thumbnail_url": url}, status=status.HTTP_200_OK)
    
class EventDeleteView(APIView):
    """
    DELETE /api/homes/<uuid:home_id>/events/<uuid:event_id>/

    User-facing delete for a stuck or unwanted session — most useful for
    an OPEN session whose engine process died mid-track. Deleting frees
    up the (device, track_id, OPEN) slot the dedup lookup uses, so a new
    physical detection reusing that same track_id no longer gets merged
    into the dead row (which is also what silently blocked new sessions
    from ever appearing while an old one sat stuck OPEN).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, home_id, event_id):
        event = DetectionEventModel.objects.filter(id=event_id, home_id=home_id).first()
        if event is None:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        was_open = event.status == "OPEN"
        event.delete()  # cascades to any related Alert rows
        return Response(
            {"deleted": True, "was_open": was_open},
            status=status.HTTP_200_OK,
        )

class HomeEventsForAssistantView(APIView):
    """
    GET /api/homes/<uuid:home_id>/events/context/?limit=50

    Called by the AI engine (not the browser) to pull recent events as
    context for the assistant's question-answering. Same data as
    HomeEventListView but IsAIEngine-gated since there's no logged-in
    user on this call path.
    """
    permission_classes = [IsAIEngine]

    def get(self, request, home_id):
        limit = int(request.query_params.get("limit", 50))
        qs = DetectionEventModel.objects.filter(
            home_id=home_id
        ).select_related("matched_member", "device").order_by("-timestamp")[:limit]

        events = [
            {
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "person_type": e.person_type,
                "person_label": e.person_label,
                "camera_location": e.camera_location,
                "event_type": e.event_type,
                "duration_seconds": e.duration_seconds,
                "event_summary": e.event_summary,
            }
            for e in qs
        ]
        return Response({"events": events}, status=status.HTTP_200_OK)