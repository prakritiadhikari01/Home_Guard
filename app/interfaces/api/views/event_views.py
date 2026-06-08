# app/interfaces/api/views/event_views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.interfaces.api.serializers.event_serializers import (
    EventIngestSerializer
)

from app.application.services.detection_event_service import (
    DetectionEventService
)


class AIEventIngestView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = (
            EventIngestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        event = (
            DetectionEventService
            .process_ai_detection(
                serializer.validated_data
            )
        )

        return Response(
            {
                "status": "success",
                "event_id": str(
                    event.id
                )
            },
            status=status.HTTP_201_CREATED
        )