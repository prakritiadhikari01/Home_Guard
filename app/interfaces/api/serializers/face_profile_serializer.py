from rest_framework import serializers

from app.infrastructure.db.models.face_profile_model import FaceProfile


class FaceProfileSerializer(serializers.ModelSerializer):

    member_id = serializers.UUIDField(
        source="home_member.id",
        read_only=True,
    )

    user_email = serializers.CharField(
        source="home_member.user.email",
        read_only=True,
    )

    class Meta:

        model = FaceProfile

        fields = [
            "id",
            "member_id",
            "user_email",
            "label_name",
            "embeddings",
            "image_url",
            "is_verified",
            "created_at",
        ]


class FaceRegistrationSerializer(serializers.Serializer):

    home_member_id = serializers.UUIDField()

    label_name = serializers.CharField()

    embeddings = serializers.DictField()