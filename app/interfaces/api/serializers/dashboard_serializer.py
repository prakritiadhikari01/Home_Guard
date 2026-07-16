from rest_framework import serializers


class DashboardHomeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class DashboardSecurityModeSerializer(serializers.Serializer):
    current = serializers.CharField()
    can_change = serializers.BooleanField()


class DashboardSummarySerializer(serializers.Serializer):
    title = serializers.CharField()
    message = serializers.CharField()


class DashboardStatsSerializer(serializers.Serializer):
    members = serializers.IntegerField()
    unknown_detections = serializers.IntegerField()
    alerts = serializers.IntegerField()
    devices_online = serializers.IntegerField()
    devices_total = serializers.IntegerField()


class DashboardLivePreviewSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    location = serializers.CharField()
    status = serializers.CharField()
    stream_url = serializers.CharField(
        allow_null=True,
        allow_blank=True,
    )
    current_detection = serializers.CharField()


class DashboardRecentEventSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    summary = serializers.CharField(
        allow_blank=True,
        allow_null=True,
    )
    device = serializers.CharField()
    timestamp = serializers.DateTimeField()


class DashboardSerializer(serializers.Serializer):

    home = DashboardHomeSerializer()

    security_mode = DashboardSecurityModeSerializer()

    summary = DashboardSummarySerializer()

    stats = DashboardStatsSerializer()

    live_preview = DashboardLivePreviewSerializer(
        many=True
    )

    recent_events = DashboardRecentEventSerializer(
        many=True
    )