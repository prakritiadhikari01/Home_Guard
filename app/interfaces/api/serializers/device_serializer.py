#app/interfaces/api/serializers/device_serializer.py
from rest_framework import serializers

from app.infrastructure.db.models.detection_event_model import DetectionEvent
from app.infrastructure.db.models.device_model import (
    Device,
)
from app.infrastructure.db.models.device_settings_model import DeviceSettings


class DeviceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device

        fields = [
            "id",
            "name",
            "device_type",
            "ip_address",
            "location",
            "stream_url",
        ]


class DeviceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device

        fields = [
            "id",
            "name",
            "device_type",
            "ip_address",
            "location",
            "status",
        ]


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id", "name", "device_type", "ip_address",
            "stream_url", "location", "status", "last_active", "created_at",
        ]
        read_only_fields = ["id", "status", "last_active", "created_at"]


class DeviceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["name", "location", "ip_address", "stream_url"]

class DeviceHealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    last_active = serializers.DateTimeField(allow_null=True)
    latency_ms = serializers.IntegerField(allow_null=True)
    fps = serializers.IntegerField(allow_null=True)
    ai_running = serializers.BooleanField()
    engine_connected = serializers.BooleanField()


class DeviceEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionEvent
        # NOTE: adjust field names to match your real DetectionEvent model.
        fields = ["id", "event_type", "label", "confidence", "alert_generated", "created_at"]

class DeviceSettingsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSettings
        fields = [
            "human_detection", "animal_detection", "vehicle_detection",
            "motion_detection", "confidence_threshold", "recording_enabled", "enabled",
        ]