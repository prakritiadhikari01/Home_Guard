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
    can_control_devices = serializers.BooleanField(required=False)
    can_manage_members = serializers.BooleanField(required=False)
    can_unlock_door = serializers.BooleanField(required=False)
    receive_alerts = serializers.BooleanField(required=False)

class HomeMemberListSerializer(serializers.Serializer):

    id = serializers.UUIDField()

    # Added: the /remove/ and /role/ URLs are keyed on <int:user_id> (the
    # auth user's PK), not the HomeMember's own UUID above. Without this
    # field the frontend has no way to build those URLs at all.
    user_id = serializers.IntegerField(source="user.id")

    email = serializers.CharField(
        source="user.email"
    )

    full_name = serializers.CharField(
        source="user.full_name"
    )
    phone = serializers.CharField(
        source="user.phone",
        allow_null=True,
        allow_blank=True,
        required=False,
    )
    role = serializers.CharField()
    can_view_dashboard = serializers.BooleanField()
    can_control_devices = serializers.BooleanField()
    can_manage_members = serializers.BooleanField()
    can_unlock_door = serializers.BooleanField()
    receive_alerts = serializers.BooleanField()
    joined_at = serializers.DateTimeField()

