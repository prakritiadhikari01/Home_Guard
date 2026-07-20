# app/application/services/home_service.py
from django.db import transaction

from app.domain.value_objects.role import Role
from app.application.services.enrollment_service import EnrollmentService
from app.infrastructure.db.repositories.django_home_repository import DjangoHomeRepository
from app.infrastructure.db.repositories.django_face_profile_repository import DjangoFaceProfileRepository


class HomeService:

    home_repository = DjangoHomeRepository()
    face_repository = DjangoFaceProfileRepository()

    @staticmethod
    @transaction.atomic
    def create_home(user, validated_data):

        home = HomeService.home_repository.create_home(
            name=validated_data["name"],
            address=validated_data["address"],
            owner=user,
        )

        HomeService.home_repository.create_home_member(
            home=home,
            user=user,
            role=Role.OWNER.value,
            can_control_devices=True,
            can_manage_members=True,
            can_unlock_door=True,
            receive_alerts=True,
        )

        return {"home": home}

    @staticmethod
    def get_user_homes(user):
        return HomeService.home_repository.get_user_homes(user)