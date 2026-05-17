from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from app.infrastructure.db.models.home_model import Home

from app.infrastructure.db.models.smart_lock_model import (
    SmartLock,
)

from app.application.services.smart_lock_service import (
    SmartLockService,
)

from app.interfaces.api.serializers.smart_lock_serializer import (
    SmartLockSerializer,
)


class UnlockDoorView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, home_id, lock_id):

        home = get_object_or_404(
            Home,
            id=home_id,
        )

        smart_lock = get_object_or_404(
            SmartLock,
            id=lock_id,
        )

        smart_lock = (
            SmartLockService.unlock_door(
                acting_user=request.user,
                home=home,
                smart_lock=smart_lock,
            )
        )

        serializer = SmartLockSerializer(
            smart_lock
        )

        return Response(serializer.data)