from django.db import transaction

from app.domain.value_objects.role import Role

from app.infrastructure.db.repositories.django_home_repository import (
    DjangoHomeRepository,
)


class HomeService:

    home_repository = DjangoHomeRepository()

    @transaction.atomic
    @staticmethod
    def create_home(user, validated_data):

        home = (
            HomeService.home_repository.create_home(
                name=validated_data["name"],
                address=validated_data["address"],
                owner=user,
            )
        )

        (
            HomeService.home_repository
            .create_home_member(
                home=home,
                user=user,
                role=Role.OWNER.value,
                can_control_devices=True,
                can_manage_members=True,
                can_unlock_door=True,
                receive_alerts=True,
            )
        )

        return home

    @staticmethod
    def get_user_homes(user):

        return (
            HomeService.home_repository
            .get_user_homes(user)
        )