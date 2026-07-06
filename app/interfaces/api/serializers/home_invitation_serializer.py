from rest_framework import serializers
class PendingInvitationSerializer(serializers.Serializer):

    id = serializers.UUIDField()

    home_id = serializers.UUIDField(
        source="home.id"
    )

    home_name = serializers.CharField(
        source="home.name"
    )

    address = serializers.CharField(
        source="home.address"
    )

    role = serializers.CharField()

    invited_at = serializers.DateTimeField(
        source="created_at"
    )