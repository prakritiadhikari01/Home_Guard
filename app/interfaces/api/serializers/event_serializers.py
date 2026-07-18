# app/interfaces/api/serializers/event_serializers.py

from rest_framework import serializers


class EventIngestSerializer(serializers.Serializer):
    """
    POST /api/events/ingest/ body.
    Fast path — called every frame. Only cheap, already-known fields belong here.
    """

    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    event_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    person_type = serializers.CharField()

    person_label = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    member_id = serializers.UUIDField(required=False, allow_null=True)
    face_profile_id = serializers.UUIDField(required=False, allow_null=True)
    confidence_score = serializers.FloatField(default=0.0)
    camera_location = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    image_url = serializers.URLField(required=False, allow_null=True)
    snapshot_url = serializers.CharField(required=False, allow_null=True)

    # Optional lightweight thumbnail — a quick still, NOT the full clip.
    # Send this immediately if you have it; it can also arrive later via enrich().
    thumbnail_url = serializers.URLField(required=False, allow_null=True)


class EventEnrichSerializer(serializers.Serializer):
    """
    PATCH /api/events/<id>/enrich/ body.
    Slow path — called once the VLM pass on the clip is done. All fields
    optional since the AI engine may only have some of them ready.
    """

    clip_url = serializers.URLField(required=False, allow_null=True)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    event_summary = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    # Free-form structured facts extracted by the VLM, e.g.
    # {"clothing": "red jacket", "carrying": "backpack"}.
    # Merged into the event's existing metadata, not a replacement.
    attributes = serializers.JSONField(required=False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError(
                "Provide at least one of: clip_url, thumbnail_url, event_summary, attributes."
            )
        return data


class DetectionEventResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    event_type = serializers.CharField()
    person_type = serializers.CharField()
    person_label = serializers.CharField(allow_null=True)
    confidence_score = serializers.FloatField()
    camera_location = serializers.CharField(allow_null=True)
    image_url = serializers.URLField(allow_null=True)
    snapshot_url = serializers.CharField(allow_null=True)
    thumbnail_url = serializers.CharField(allow_null=True)
    clip_url = serializers.CharField(allow_null=True)
    event_summary = serializers.CharField(allow_null=True)
    is_enriched = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
    duration_seconds = serializers.IntegerField()
    metadata = serializers.JSONField()
