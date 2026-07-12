# app/interfaces/api/views/smart_lock_views.py
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device

from app.application.services.smart_lock_service import SmartLockService

from app.interfaces.api.serializers.smart_lock_serializer import (
    SmartLockSerializer,
    SmartLockDetailSerializer,
)


class UnlockDoorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id, lock_id):
        home = get_object_or_404(Home, id=home_id)
        device = get_object_or_404(Device, id=lock_id, home=home)

        smart_lock = SmartLockService.manual_unlock(acting_user=request.user, device=device)
        return Response(SmartLockSerializer(smart_lock).data)


class LockDoorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id, lock_id):
        home = get_object_or_404(Home, id=home_id)
        device = get_object_or_404(Device, id=lock_id, home=home)

        smart_lock = SmartLockService.manual_lock(acting_user=request.user, device=device)
        return Response(SmartLockSerializer(smart_lock).data)


class SmartLockDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, home_id, lock_id):
        home = get_object_or_404(Home, id=home_id)
        device = get_object_or_404(Device, id=lock_id, home=home)

        smart_lock = SmartLockService.get_lock_detail(device)
        return Response(SmartLockDetailSerializer(smart_lock).data)