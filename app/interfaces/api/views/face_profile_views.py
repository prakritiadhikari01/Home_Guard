from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from app.interfaces.api.serializers.face_profile_serializer import (
    FaceRegistrationSerializer
)

from app.application.services.face_registration_service import (
    FaceRegistrationService
)


class RegisterFaceView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = FaceRegistrationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        face_profile = (
            FaceRegistrationService.register_face(
                user=request.user,
                home_id=data["home_id"],
                label_name=data["label_name"],
                image_base64=data["image"]
            )
        )

        return Response(
            {
                "message": "Face registered",
                "face_profile_id": face_profile.id
            },
            status=status.HTTP_201_CREATED
        )