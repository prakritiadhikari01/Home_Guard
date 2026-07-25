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
    UnlockAttemptSerializer,
)


class UnlockDoorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id, lock_id):
        home = get_object_or_404(Home, id=home_id)
        device = get_object_or_404(Device, id=lock_id, home=home)

        smart_lock, verification_id = SmartLockService.request_unlock(
            acting_user=request.user,
            device=device,
        )
        data = UnlockAttemptSerializer({
            "status": smart_lock.status,
            "verification_id": verification_id,
            "message": "Look at the camera on the door.",
        }).data
        return Response(data, status=202)


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