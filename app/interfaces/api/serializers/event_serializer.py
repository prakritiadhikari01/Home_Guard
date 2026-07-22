# app/interfaces/api/serializers/event_serializers.py
from rest_framework import serializers


class EventOpenSerializer(serializers.Serializer):
    """POST /api/events/open/ — motion + tracking assigns a track_id."""
    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    track_id = serializers.CharField()
    started_at = serializers.DateTimeField(required=False)

    pipeline_stage = serializers.CharField(required=False)
    event_type = serializers.CharField(required=False)
    person_type = serializers.CharField(required=False)
    person_label = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    member_id = serializers.UUIDField(required=False, allow_null=True)
    face_profile_id = serializers.UUIDField(required=False, allow_null=True)
    confidence_score = serializers.FloatField(default=0.0)
    camera_location = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_null=True)
    snapshot_url = serializers.CharField(required=False, allow_null=True)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False)


class EventProgressSerializer(serializers.Serializer):
    """PATCH /api/events/<id>/progress/ — called repeatedly as recognition resolves."""
    pipeline_stage = serializers.CharField(required=False)
    event_type = serializers.CharField(required=False)
    person_type = serializers.CharField(required=False)
    person_label = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    member_id = serializers.UUIDField(required=False, allow_null=True)
    face_profile_id = serializers.UUIDField(required=False, allow_null=True)
    confidence_score = serializers.FloatField(required=False)
    image_url = serializers.URLField(required=False, allow_null=True)
    snapshot_url = serializers.CharField(required=False, allow_null=True)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    last_seen_at = serializers.DateTimeField(required=False)
    metadata = serializers.JSONField(required=False)


class EventCloseSerializer(serializers.Serializer):
    """PATCH /api/events/<id>/close/ — track lost / session timeout."""
    ended_at = serializers.DateTimeField(required=False)


class EventEnrichSerializer(serializers.Serializer):
    """PATCH /api/events/<id>/enrich/ body. Unchanged from before."""
    clip_url = serializers.URLField(required=False, allow_null=True)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    event_summary = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    attributes = serializers.JSONField(required=False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError(
                "Provide at least one of: clip_url, thumbnail_url, event_summary, attributes."
            )
        return data


class DetectionEventResponseSerializer(serializers.Serializer):
    """Generic echo-back shape used by open/progress/close/enrich responses."""
    id = serializers.UUIDField()
    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    track_id = serializers.CharField()
    status = serializers.CharField()
    pipeline_stage = serializers.CharField()
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
    started_at = serializers.DateTimeField(allow_null=True)
    last_seen_at = serializers.DateTimeField(allow_null=True)
    ended_at = serializers.DateTimeField(allow_null=True)
    duration_seconds = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    metadata = serializers.JSONField()


class DetectionEventListSerializer(serializers.ModelSerializer):
    """
    Read-model for Timeline / Alerts pages. Computes category + badge_level +
    human title/subtitle server-side so every client (web, future mobile)
    renders identical labels. Import DetectionEvent model lazily to avoid
    circular imports at module load time.
    """
    member_name = serializers.SerializerMethodField()
    camera_name = serializers.CharField(source="device.name", default=None)
    category = serializers.SerializerMethodField()
    badge_level = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()

    class Meta:
        from app.infrastructure.db.models.detection_event_model import DetectionEvent
        model = DetectionEvent
        fields = [
            "id", "status", "pipeline_stage", "event_type", "person_type",
            "person_label", "member_name", "camera_name", "camera_location",
            "confidence_score", "thumbnail_url", "clip_url", "event_summary",
            "is_enriched", "duration_seconds", "timestamp",
            "category", "badge_level", "title", "subtitle",
        ]

    def get_member_name(self, obj):
        return obj.matched_member.user.full_name if obj.matched_member_id else None

    def get_category(self, obj):
        if obj.person_type == "INTRUDER":
            return "alerts"
        if obj.event_type in ("DOOR_LOCKED", "DOOR_UNLOCKED"):
            return "doors"
        if obj.event_type == "VEHICLE_DETECTED" or obj.person_type == "VEHICLE":
            return "vehicles"
        if obj.event_type == "MOTION_DETECTED":
            return "animals"
        if obj.person_type == "KNOWN":
            return "recognized"
        if obj.person_type == "UNKNOWN":
            return "unknown"
        return "all"

    def get_badge_level(self, obj):
        if obj.person_type == "INTRUDER":
            return "critical"
        if obj.event_type == "DOOR_LOCKED" or obj.person_type == "KNOWN":
            return "success"
        return "warning"

    def get_title(self, obj):
        loc = obj.camera_location or "camera"
        member = self.get_member_name(obj)
        if obj.status == "OPEN":
            return f"Identifying activity at {loc}..."
        if obj.person_type == "INTRUDER":
            return f"Intruder alert · {loc}"
        if obj.event_type == "DOOR_UNLOCKED":
            return f"{member or 'Unknown user'} unlocked {loc}"
        if obj.event_type == "DOOR_LOCKED":
            return f"{member or 'Door'} locked · {loc}"
        if obj.event_type == "VEHICLE_DETECTED":
            return f"Vehicle detected · {loc}"
        if obj.event_type == "MOTION_DETECTED":
            return f"Motion detected · {loc}"
        if obj.person_type == "KNOWN":
            return f"{member or obj.person_label} entered {loc}"
        if obj.person_type == "UNKNOWN":
            return f"Unknown person at {loc}"
        return f"{obj.event_type.replace('_', ' ').title()} · {loc}"

    def get_subtitle(self, obj):
        if obj.event_summary:
            return obj.event_summary
        conf = round((obj.confidence_score or 0) * 100)
        if obj.status == "OPEN":
            return "Session in progress..."
        if obj.person_type in ("KNOWN", "UNKNOWN"):
            return f"Facial recognition · {conf}%"
        if obj.event_type == "VEHICLE_DETECTED":
            return f"Vehicle classification · {conf}%"
        return f"Confidence · {conf}%"


class AlertSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    severity = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    resolved_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
