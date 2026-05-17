from app.domain.repositories.home_repository import (
    AbstractHomeRepository,
)

from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.home_model import Home


class DjangoHomeRepository(AbstractHomeRepository):

    def create_home(self, **kwargs):
        return Home.objects.create(**kwargs)

    def create_home_member(self, **kwargs):
        return HomeMember.objects.create(**kwargs)

    def get_user_homes(self, user):
        return (
            HomeMember.objects
            .filter(user=user)
            .select_related("home")
        )