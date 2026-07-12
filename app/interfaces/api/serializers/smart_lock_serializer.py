# app/interfaces/api/serializers/smart_lock_serializer.py
from rest_framework import serializers

from app.infrastructure.db.models.smart_lock_model import SmartLock


class SmartLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartLock
        fields = ["id", "status", "last_unlocked_by", "updated_at"]


class SmartLockDetailSerializer(serializers.ModelSerializer):
    last_unlocked_by_name = serializers.CharField(
        source="last_unlocked_by.user.get_full_name",
        read_only=True,
        default=None,
    )

    class Meta:
        model = SmartLock
        # NOTE: add battery_level to your SmartLock model if it's not there yet.
        fields = ["id", "status", "last_unlocked_by_name", "last_unlocked_at", "battery_level"]