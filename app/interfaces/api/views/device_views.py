# app/interfaces/api/views/device_views.py
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework import status

from app.infrastructure.db.models.home_model import Home

from app.application.services.device_service import (
    DeviceService,
)

from app.interfaces.api.serializers.device_serializer import (
    DeviceCreateSerializer,
    DeviceListSerializer,
)
from app.infrastructure.external.ai_client import AIClient


class RegisterDeviceView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):

        serializer = DeviceCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        home = get_object_or_404(
            Home,
            id=home_id,
        )

        device = (
            DeviceService.register_device(
                acting_user=request.user,
                home=home,
                validated_data=serializer.validated_data,
            )
        )

        return Response(
            DeviceCreateSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )


class HomeDevicesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, home_id):

        home = get_object_or_404(
            Home,
            id=home_id,
        )

        devices = (
            DeviceService.get_home_devices(home)
        )

        serializer = DeviceListSerializer(
            devices,
            many=True,
        )

        return Response(serializer.data)