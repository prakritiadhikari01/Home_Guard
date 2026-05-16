from rest_framework import serializers
from app.domain.value_objects.role import Role


class AddHomeMemberSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()

    role = serializers.ChoiceField(
        choices=Role.choices(),
        default=Role.MEMBER.value,
    )