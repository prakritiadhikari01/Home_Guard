#app/interfaces/api/serializers/home_member_serializer.py
from rest_framework import serializers

from app.domain.value_objects.role import Role


class AddHomeMemberSerializer(serializers.Serializer):

    email = serializers.EmailField()

    role = serializers.ChoiceField(
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )


class UpdateMemberRoleSerializer(serializers.Serializer):

    role = serializers.ChoiceField(
        choices=Role.choices()
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