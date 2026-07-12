##app/interfaces/api/serializers/setting_serializer.py
from rest_framework import serializers

from app.infrastructure.db.models.home_settings_model import HomeSettings
from app.infrastructure.db.models.user_settings_model import UserSettings
from app.infrastructure.db.models.device_settings_model import DeviceSettings


class HomeSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeSettings
        exclude = ["id", "home"]


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSettings
        exclude = ["id", "user"]


class DeviceSettingsSerializer(serializers.ModelSerializer):

    device_name = serializers.CharField(
        source="device.name",
        read_only=True,
    )

    class Meta:
        model = DeviceSettings
        exclude = ["id", "device"]


class SettingsSerializer(serializers.Serializer):

    home_settings = HomeSettingsSerializer()

    user_settings = UserSettingsSerializer()

    device_settings = DeviceSettingsSerializer(
        many=True
    )