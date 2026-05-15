from rest_framework import serializers

from app.infrastructure.db.models.home_model import Home


class HomeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Home
        fields = ["id", "name", "address"]


class HomeListSerializer(serializers.Serializer):

    id = serializers.UUIDField(source="home.id")

    name = serializers.CharField(source="home.name")

    role = serializers.CharField()