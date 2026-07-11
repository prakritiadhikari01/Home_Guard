#app/interfaces/api/views/enrollment_views.py
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from app.application.services.enrollment_service import (
    EnrollmentService,
)

from app.interfaces.api.serializers.enrollment_serializer import (
    CompleteEnrollmentSerializer,
    EnrollmentStatusSerializer,
)

class EnrollmentStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        session_id,
    ):

        session = (
            EnrollmentService.get_status(
                session_id
            )
        )

        serializer = EnrollmentStatusSerializer(
            session
        )

        return Response(serializer.data)


class CompleteEnrollmentView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = CompleteEnrollmentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = (
            EnrollmentService.complete_enrollment(
                session_id=serializer.validated_data[
                    "session_id"
                ],
                embeddings=serializer.validated_data[
                    "embeddings"
                ],
            )
        )

        return Response(
            {
                "message": "Enrollment completed successfully.",
                "home_member_id": result[
                    "member"
                ].id,
                "face_profile_id": result[
                    "face_profile"
                ].id,
                "session_id": result[
                    "session"
                ].id,
            },
            status=status.HTTP_200_OK,
        )


class FailEnrollmentView(APIView):

    permission_classes = []

    def post(
        self,
        request,
        session_id,
    ):

        reason = request.data.get(
            "reason",
            "Unknown error",
        )

        EnrollmentService.fail_enrollment(
            session_id=session_id,
            reason=reason,
        )

        return Response(
            {
                "message": "Enrollment marked as failed.",
            },
            status=status.HTTP_200_OK,
        )