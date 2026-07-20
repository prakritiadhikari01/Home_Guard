# app/interfaces/api/face_permissions.py
from rest_framework.permissions import BasePermission
from app.infrastructure.db.repositories.django_face_profile_repository import (
    DjangoFaceProfileRepository,
)


class IsFaceEnrolled(BasePermission):
    message = "Face enrollment required before this action."
    code = "face_enrollment_required"   
    face_repository = DjangoFaceProfileRepository()

    def has_permission(self, request, view):
        return self.face_repository.exists(request.user, verified_only=True)