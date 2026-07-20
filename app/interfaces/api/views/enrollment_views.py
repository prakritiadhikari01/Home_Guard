#app/interfaces/api/views/enrollment_views.py
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from rest_framework import status

from app.application.services.enrollment_service import (
    EnrollmentService,
)

from app.interfaces.api.permissions.service_permissions import IsAIEngine
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
    """
    Called by the AI Engine (Windows box) once enrollment finishes —
    not by the browser. Auth is the shared-secret X-API-Key, not a user
    JWT, so there's no request.user to check ownership against. The
    session_id itself is the only credential needed here: it's a UUID
    created server-side by StartEnrollmentView and never exposed to
    anyone but the enrolling user's browser + the AI Engine relaying it
    back, so knowing it is sufficient authorization to complete it.
    """
    permission_classes = [IsAIEngine]
 
    def post(self, request):
        serializer = CompleteEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        result = EnrollmentService.complete_enrollment(
            session_id=serializer.validated_data["session_id"],
            embeddings=serializer.validated_data["embeddings"],
        )
 
        return Response(
            {
                "message": "Enrollment completed successfully.",
                "face_profile_id": result["face_profile"].id,
                "session_id": result["session"].id,
            },
            status=status.HTTP_200_OK,
        )
class StartEnrollmentView(APIView):
    """Triggered from User Settings — enroll or re-scan face anytime."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = EnrollmentService.start_enrollment(user=request.user)
        return Response({
            "session_id": session.id,
            "status": session.status,
            "scan_url": f"/scan-face/?session={session.id}",
        })

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