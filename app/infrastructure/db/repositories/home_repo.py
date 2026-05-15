from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.home_model import Home


class HomeRepository:

    @staticmethod
    def create_home(**kwargs):
        return Home.objects.create(**kwargs)

    @staticmethod
    def create_home_member(**kwargs):
        return HomeMember.objects.create(**kwargs)

    @staticmethod
    def get_user_homes(user):
        return HomeMember.objects.filter(user=user).select_related("home")