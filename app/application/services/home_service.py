from app.domain.value_objects.role import Role
from app.infrastructure.db.repositories.home_repo import HomeRepository


class HomeService:

    @staticmethod
    def create_home(user, validated_data):

        home = HomeRepository.create_home(
            name=validated_data["name"],
            address=validated_data["address"],
            owner=user,
        )

        HomeRepository.create_home_member(
            home=home,
            user=user,
            role=Role.OWNER.value,
            can_control_devices=True,
            can_manage_members=True,
            can_unlock_door=True,
            receive_alerts=True,
        )

        return home

    @staticmethod
    def get_user_homes(user):
        return HomeRepository.get_user_homes(user)