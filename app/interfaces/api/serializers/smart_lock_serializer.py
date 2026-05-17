from rest_framework import serializers

from app.infrastructure.db.models.smart_lock_model import (
    SmartLock,
)


class SmartLockSerializer(serializers.ModelSerializer):

    class Meta:
        model = SmartLock

        fields = [
            "id",
            "status",
            "last_unlocked_by",
            "updated_at",
        ]