#app/interfaces/api/serializers/home_serializer.py
from rest_framework import serializers

from app.infrastructure.db.models.home_model import Home

from app.domain.value_objects.security_mode import SecurityMode

class HomeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Home
        fields = ["id", "name", "address"]


class HomeListSerializer(serializers.Serializer):

    id = serializers.UUIDField(source="home.id")

    name = serializers.CharField(source="home.name")

    role = serializers.CharField()

    security_mode = serializers.CharField(source="home.security_mode")


class SecurityModeUpdateSerializer(serializers.Serializer):
    security_mode = serializers.ChoiceField(choices=SecurityMode.choices())