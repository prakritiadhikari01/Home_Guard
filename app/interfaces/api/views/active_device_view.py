# app/interfaces/api/views/active_device_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from app.infrastructure.db.models.device_model import Device
from app.domain.value_objects.device_type import DeviceType
from app.domain.value_objects.device_status import DeviceStatus


class ActiveDeviceListView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        cameras = (
            Device.objects
            .filter(
                device_type=DeviceType.CAMERA.value,
                status=DeviceStatus.ONLINE.value
            )
            .select_related("home")
        )

        data = []

        for camera in cameras:

            data.append(
                {
                    "id": str(camera.id),
                    "name": camera.name,
                    "home_id": str(camera.home.id),
                    "stream_url": camera.stream_url,
                    "location": camera.location
                }
            )

        return Response(
            {
                "count": len(data),
                "cameras": data
            }
        )