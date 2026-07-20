# app/interfaces/api/serializers/face_profile_serializer.py
from rest_framework import serializers
from app.infrastructure.db.models.face_profile_model import FaceProfile


class FaceProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = FaceProfile
        fields = [
            "id", "user_id", "user_email",
            "label_name", "embeddings", "image_url",
            "is_verified", "created_at",
        ]


class FaceRegistrationSerializer(serializers.Serializer):
    label_name = serializers.CharField()
    embeddings = serializers.DictField()