# app/interfaces/api/views/face_list_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers

from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.interfaces.api.serializers.face_profile_serializer import FaceProfileSerializer


class FaceListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        faces = FaceProfile.objects.all().order_by("-created_at")
        faces = faces.exclude(embedding__isnull=True)

        serializer = FaceProfileSerializer(faces, many=True)

        return Response({
            "count": faces.count(),
            "faces": serializer.data
        })