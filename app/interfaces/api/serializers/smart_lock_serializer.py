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
        fields = [
            "id",
            "status",
            "last_unlocked_by_name",
            "last_unlocked_at",
            "current_verification_id",
            "last_access_result",
        ]


class UnlockAttemptSerializer(serializers.Serializer):
    status = serializers.CharField()
    verification_id = serializers.UUIDField()
    message = serializers.CharField()