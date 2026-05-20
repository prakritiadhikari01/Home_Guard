from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from app.infrastructure.db.repositories.django_face_profile_repository import (
    DjangoFaceProfileRepository
)

from app.infrastructure.db.models.home_model import Home


class FaceSaveView(APIView):

    permission_classes = [IsAuthenticated]

    face_repo = DjangoFaceProfileRepository()

    def post(self, request):

        data = request.data

        home_id = data.get("home_id")
        label_name = data.get("label_name")
        embedding = data.get("embedding")

        if not embedding:
            return Response(
                {"error": "No embedding provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        home = Home.objects.get(id=home_id)

        face_profile = self.face_repo.create_face_profile(
            user=request.user,
            home=home,
            label_name=label_name,
            embedding=embedding,
            is_verified=True
        )

        return Response(
            {
                "message": "Face saved successfully",
                "face_profile_id": str(face_profile.id)
            },
            status=status.HTTP_201_CREATED
        )