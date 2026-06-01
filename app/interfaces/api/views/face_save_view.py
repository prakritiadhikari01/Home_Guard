from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.home_member_model import HomeMember


class FaceSaveView(APIView):

    permission_classes = []

    def post(self, request):

        try:

            data = request.data

            home_member_id = data.get("home_member_id")
            label_name = data.get("label_name")
            embedding = data.get("embedding")

            if not embedding:
                return Response(
                    {"error": "No embedding provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            member = HomeMember.objects.get(
                id=home_member_id
            )

            face_profile = FaceProfile.objects.create(
                home_member=member,
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

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )