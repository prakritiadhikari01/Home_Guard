from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.enrollment_service import (
    EnrollmentService,
)


class FaceSaveView(APIView):

    permission_classes = []

    def post(self, request):

        session_id = request.data.get("session_id")
        embeddings = request.data.get("embeddings")

        if not session_id:
            return Response(
                {
                    "error": "session_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not embeddings:
            return Response(
                {
                    "error": "embeddings are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            result = (
                EnrollmentService.complete_enrollment(
                    session_id=session_id,
                    embeddings=embeddings,
                )
            )

            return Response(
                {
                    "message": "Enrollment completed successfully.",
                    "session_id": str(
                        result["session"].id
                    ),
                    "home_member_id": str(
                        result["member"].id
                    ),
                    "face_profile_id": str(
                        result["face_profile"].id
                    ),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )