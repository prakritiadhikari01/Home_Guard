from rest_framework import serializers

from app.interfaces.api.serializers.home_serializer import HomeListSerializer
from app.interfaces.api.serializers.home_member_serializer import (
    HomeMemberListSerializer,
)
from app.interfaces.api.serializers.device_serializer import DeviceListSerializer
from app.interfaces.api.serializers.smart_lock_serializer import (
    SmartLockSerializer,
)
from app.interfaces.api.serializers.event_serializers import (
   EventIngestSerializer,
)


class DashboardStatsSerializer(serializers.Serializer):

    members = serializers.IntegerField()

    unknown_detections = serializers.IntegerField()

    alerts = serializers.IntegerField()

    devices_online = serializers.IntegerField()

    devices_total = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):

    home = HomeListSerializer()

    security_mode = serializers.CharField()

    stats = DashboardStatsSerializer()

    members = HomeMemberListSerializer(many=True)

    devices = DeviceListSerializer(many=True)

    smart_locks = SmartLockSerializer(many=True)

    recent_events = EventIngestSerializer(many=True)