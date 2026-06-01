# app/interfaces/api/views/event_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.application.services.detection_event_service import (
    DetectionEventService
)


class DetectionEventAPIView(APIView):

    permission_classes = []

    authentication_classes = []

    def post(self, request):

        try:

            event = (
                DetectionEventService
                .process_ai_detection(
                    request.data
                )
            )

            return Response(
                {
                    "status": "success",
                    "event_id": event.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )