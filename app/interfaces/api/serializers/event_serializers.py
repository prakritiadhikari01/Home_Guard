from rest_framework import serializers

class EventIngestSerializer(serializers.Serializer):
    home_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    image = serializers.CharField()           # base64-encoded image
    timestamp = serializers.DateTimeField()
    event_type = serializers.CharField()      # e.g., "motion", "person_detected"
    confidence_score = serializers.FloatField()
    person_type = serializers.CharField()  # e.g., "KNOWN", "UNKNOWN"
    member_id = serializers.UUIDField()   
    face_id = serializers.UUIDField()    
    