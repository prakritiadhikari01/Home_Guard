from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.home_service import HomeService
from app.interfaces.api.serializers.home_serializer import (
    HomeCreateSerializer,
    HomeListSerializer,
)


class HomeCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = HomeCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        home = HomeService.create_home(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        return Response(
            HomeCreateSerializer(home).data,
            status=status.HTTP_201_CREATED,
        )


class UserHomesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        homes = HomeService.get_user_homes(request.user)

        serializer = HomeListSerializer(homes, many=True)

        return Response(serializer.data)