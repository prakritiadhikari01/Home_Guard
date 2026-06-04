#app/interfaces/api/serializers/device_serializer.py
from rest_framework import serializers

from app.infrastructure.db.models.device_model import (
    Device,
)


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