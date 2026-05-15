from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "profile_image",
            "status",
            "created_at",
            "last_login",
        ]
        read_only_fields = ["id", "created_at", "last_login"]