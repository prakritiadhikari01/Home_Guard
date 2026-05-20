from django.shortcuts import get_object_or_404

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.repositories.django_face_profile_repository import (
    DjangoFaceProfileRepository
)

from app.infrastructure.external.ai_client import AIClient


class FaceRegistrationService:

    face_repo = DjangoFaceProfileRepository()

    @staticmethod
    def register_face(
        user,
        home_id,
        label_name,
        image_base64
    ):

        home = get_object_or_404(
            Home,
            id=home_id
        )

        ai_response = AIClient.extract_embedding(
            image_base64
        )

        embedding = ai_response.get("embedding")

        if not embedding:
            raise Exception(
                "No face detected"
            )

        face_profile = (
            FaceRegistrationService.face_repo.create_face_profile(
                user=user,
                home=home,
                label_name=label_name,
                embedding=embedding,
                is_verified=True
            )
        )

        return face_profile