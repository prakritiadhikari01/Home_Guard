from rest_framework import serializers

class EventIngestSerializer(serializers.Serializer):
    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    image = serializers.CharField()           # base64-encoded image
    timestamp = serializers.DateTimeField()
