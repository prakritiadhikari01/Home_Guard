from rest_framework import serializers


class FaceRegistrationSerializer(serializers.Serializer):

    home_id = serializers.UUIDField()

    label_name = serializers.CharField()

    image = serializers.CharField()