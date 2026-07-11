from rest_framework import serializers

from app.domain.value_objects.enrollment_status import (
    EnrollmentStatus,
)


class StartEnrollmentSerializer(serializers.Serializer):

    invitation_id = serializers.UUIDField()


class CompleteEnrollmentSerializer(serializers.Serializer):

    session_id = serializers.UUIDField()

    embeddings = serializers.JSONField()

    def validate_embeddings(self, value):

        required_poses = {
            "CENTER",
            "LEFT",
            "RIGHT",
            "UP",
            "DOWN",
        }

        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Embeddings must be an object."
            )

        missing = required_poses - set(value.keys())

        if missing:
            raise serializers.ValidationError(
                f"Missing poses: {', '.join(sorted(missing))}"
            )

        return value


class EnrollmentStatusSerializer(serializers.Serializer):

    session_id = serializers.UUIDField(
        source="id",
    )

    status = serializers.CharField()

    started_at = serializers.DateTimeField()

    completed_at = serializers.DateTimeField(
        allow_null=True,
    )

    failure_reason = serializers.CharField()

    ai_engine = serializers.CharField()

    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["status"] = instance.status

        data["is_completed"] = (
            instance.status
            == EnrollmentStatus.COMPLETED.value
        )

        data["is_running"] = (
            instance.status
            == EnrollmentStatus.RUNNING.value
        )

        return data