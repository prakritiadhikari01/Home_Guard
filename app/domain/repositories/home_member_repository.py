from abc import ABC, abstractmethod


class AbstractHomeMemberRepository(ABC):

    @abstractmethod
    def get_membership(self, home, user):
        pass

    @abstractmethod
    def member_exists(self, home, user):
        pass

    @abstractmethod
    def create_member(self, **kwargs):
        pass

    @abstractmethod
    def get_home_members(self, home):
        pass

    @abstractmethod
    def remove_member(self, home, user):
        pass

    @abstractmethod
    def update_role(
        self,
        membership,
        role,
        permissions,
    ):
        pass