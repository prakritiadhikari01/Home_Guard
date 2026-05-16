from rest_framework import serializers
from app.domain.value_objects.role import Role


class AddHomeMemberSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()

    role = serializers.ChoiceField(
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )

class HomeMemberListSerializer(serializers.Serializer):

    id = serializers.UUIDField()

    email = serializers.CharField(
        source="user.email"
    )

    full_name = serializers.CharField(
        source="user.full_name"
    )

    role = serializers.CharField()

    joined_at = serializers.DateTimeField()