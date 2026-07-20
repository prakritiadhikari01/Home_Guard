#app/interfaces/api/views/home_invitation_view.py
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.application.services.home_invitation_service import (
    HomeInvitationService,
)

from app.infrastructure.db.models.home_invitation_model import (
    HomeInvitation,
)
from app.interfaces.api.permissions.face_permissions import IsFaceEnrolled
from app.interfaces.api.serializers.home_invitation_serializer import PendingInvitationSerializer


class PendingInvitationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        invitations = (
            HomeInvitationService.get_pending_invitations(
                request.user
            )
        )

        serializer = PendingInvitationSerializer(
            invitations,
            many=True,
        )

        return Response(serializer.data)


class AcceptInvitationView(APIView):
    
    permission_classes = [IsAuthenticated, IsFaceEnrolled]

    def post(self, request, invitation_id):

        invitation = get_object_or_404(
            HomeInvitation, id=invitation_id, email=request.user.email, status="pending",
        )
        
        result = HomeInvitationService.accept_invitation(invitation, request.user)

        return Response({
            "message": "Home joined.",
            "home_id": str(result["member"].home_id),
        })

class RejectInvitationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        invitation_id,
    ):
        invitation = get_object_or_404(
            HomeInvitation,
            id=invitation_id,
            email=request.user.email,
            status="pending",
        )

        HomeInvitationService.reject_invitation(
            invitation
        )

        return Response(
            {
                "message": "Invitation rejected"
            }
        )