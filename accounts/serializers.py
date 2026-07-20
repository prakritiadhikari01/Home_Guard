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

class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()

    def validate(self, attrs):

        user = self.context["user"]

        if not user.check_password(
            attrs["old_password"]
        ):
            raise serializers.ValidationError(
                {
                    "old_password":
                    "Old password is incorrect."
                }
            )

        if (
            attrs["new_password"]
            != attrs["confirm_password"]
        ):
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        return attrs

    def save(self):

        user = self.context["user"]

        user.set_password(
            self.validated_data["new_password"]
        )
        user.save()

        return user