# app/interfaces/api/views/face_list_view.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from app.interfaces.api.permissions.service_permissions import IsAIEngine
from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.home_model import Home
from app.interfaces.api.serializers.face_profile_serializer import FaceProfileSerializer
from app.infrastructure.db.repositories.django_face_profile_repository import DjangoFaceProfileRepository
from app.infrastructure.db.repositories.django_home_member_repository import DjangoHomeMemberRepository


class FaceListView(APIView):
    """Legacy/global listing — no longer used for recognition (superseded
    by HomeFacesView below). Left secured in case it's used for admin/debug."""

    permission_classes = [IsAIEngine]

    def get(self, request):
        faces = FaceProfile.objects.exclude(embeddings__isnull=True).order_by("-created_at")
        serializer = FaceProfileSerializer(faces, many=True)
        return Response({"count": faces.count(), "faces": serializer.data})


class HomeFacesView(APIView):
    """
    GET /api/homes/<uuid:home_id>/faces/

    Called by the AI Engine's KnownFacesStore.refresh_home(home_id) — returns
    only the face profiles of users who are members of THIS home, so
    recognition never crosses home boundaries.
    """

    permission_classes = [IsAIEngine]

    def get(self, request, home_id):
        home = get_object_or_404(Home, id=home_id)

        profiles = DjangoFaceProfileRepository.get_home_profiles(home)
        members_by_user_id = {
            m.user_id: m
            for m in DjangoHomeMemberRepository().get_home_members(home)
        }

        faces = []
        for profile in profiles:
            member = members_by_user_id.get(profile.user_id)
            faces.append({
                "id": str(profile.id),
                "user_id": profile.user_id,
                "member_id": str(member.id) if member else None,
                "label_name": profile.label_name,
                "embeddings": profile.embeddings,
            })

        return Response({"count": len(faces), "faces": faces})