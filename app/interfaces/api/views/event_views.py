from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from app.application.services.event_service import EventService
from app.interfaces.api.serializers.event_serializers import EventIngestSerializer

class EventIngestView(APIView):
    permission_classes = [AllowAny]  # Cameras may not authenticate

    def post(self, request):
        serializer = EventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Validate Home and Device
        home = get_object_or_404(Home, id=data["home_id"])
        device = get_object_or_404(Device, id=data["device_id"], home=home)

        # Process the event (AI analysis and access logic)
        EventService.process_event(
            home=home,
            device=device,
            image_base64=data["image"],
            event_timestamp=data["timestamp"]
        )
        return Response({"status": "Event processed"}, status=status.HTTP_201_CREATED)
