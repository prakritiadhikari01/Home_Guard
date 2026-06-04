from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.detection_event_service import (
    DetectionEventService
)


class AIEventIngestView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        try:

            event = (
                DetectionEventService.process_ai_detection(
                    request.data
                )
            )

            return Response(
                {
                    "status": "success",
                    "event_id": str(event.id)
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )