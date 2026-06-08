# app/interfaces/api/serializers/event_serializers.py

from rest_framework import serializers


class EventIngestSerializer(
    serializers.Serializer
):

    home_id = (
        serializers.UUIDField()
    )

    device_id = (
        serializers.UUIDField()
    )

    event_type = (
        serializers.CharField()
    )

    timestamp = (
        serializers.DateTimeField()
    )

    person_type = (
        serializers.CharField()
    )

    person_label = (
        serializers.CharField(
            required=False,
            allow_null=True,
            allow_blank=True
        )
    )

    member_id = (
        serializers.UUIDField(
            required=False,
            allow_null=True
        )
    )

    face_profile_id = (
        serializers.UUIDField(
            required=False,
            allow_null=True
        )
    )

    confidence_score = (
        serializers.FloatField(
            default=0.0
        )
    )

    camera_location = (
        serializers.CharField(
            required=False,
            allow_null=True,
            allow_blank=True
        )
    )

    image_url = (
        serializers.URLField(
            required=False,
            allow_null=True
        )
    )