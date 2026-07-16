# app/interfaces/api/views/device_views.py
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from app.application.services.settings_service import SettingsService
from app.infrastructure.db.models.device_settings_model import DeviceSettings
from app.infrastructure.db.models.home_model import Home

from app.application.services.device_service import DeviceEventQueryService, DeviceHealthService, DeviceService

from app.interfaces.api.serializers.device_serializer import (
    DeviceCreateSerializer,
    DeviceEventSerializer,
    DeviceHealthSerializer,
    DeviceListSerializer,
    DeviceDetailSerializer,
    DeviceSettingsDetailSerializer,
    DeviceUpdateSerializer,
)


class RegisterDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):
        serializer = DeviceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        home = get_object_or_404(Home, id=home_id)

        device = DeviceService.register_device(
            acting_user=request.user,
            home=home,
            validated_data=serializer.validated_data,
        )

        return Response(DeviceCreateSerializer(device).data, status=status.HTTP_201_CREATED)


class HomeDevicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id):
        home = get_object_or_404(Home, id=home_id)
        DeviceService._require_membership(request.user, home)

        devices = DeviceService.get_home_devices(home)
        return Response(DeviceListSerializer(devices, many=True).data)


class DeviceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        DeviceService._require_membership(request.user, home)

        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DeviceDetailSerializer(device).data)

    def patch(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeviceUpdateSerializer(device, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # update_device already enforces can_control_devices via
        # DeviceService._get_membership_or_raise — no separate check needed here.
        updated = DeviceService.update_device(request.user, home, device, serializer.validated_data)
        return Response(DeviceDetailSerializer(updated).data)

    def delete(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        # delete_device already enforces can_control_devices via
        # DeviceService._get_membership_or_raise — no separate check needed here.
        DeviceService.delete_device(request.user, home, device)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceHealthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        DeviceService._require_membership(request.user, home)

        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        health = DeviceHealthService.get_health(device)
        return Response(DeviceHealthSerializer(health).data)


class DeviceEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        DeviceService._require_membership(request.user, home)

        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        events = DeviceEventQueryService.get_recent_events(device)
        return Response(DeviceEventSerializer(events, many=True).data)


class DeviceRestartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        # restart_device already enforces can_control_devices via
        # DeviceService._get_membership_or_raise — no separate check needed here.
        DeviceService.restart_device(request.user, home, device)
        return Response({"message": "Restart requested"})
    


class DeviceSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        DeviceService._require_membership(request.user, home)

        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        settings_obj = get_object_or_404(DeviceSettings, device=device)
        return Response(DeviceSettingsDetailSerializer(settings_obj).data)

    def patch(self, request, home_id, device_id):
        home = get_object_or_404(Home, id=home_id)
        # Writing settings should require control permission, not just membership.
        DeviceService._get_membership_or_raise(request.user, home)

        device = DeviceService.get_device(home, device_id)
        if not device:
            return Response({"detail": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        settings_obj = get_object_or_404(DeviceSettings, device=device)
        serializer = DeviceSettingsDetailSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = SettingsService.update_device_settings(settings_obj, serializer.validated_data)
        return Response(DeviceSettingsDetailSerializer(updated).data)