from abc import ABC, abstractmethod


class AbstractHomeRepository(ABC):

    @abstractmethod
    def create_home(self, **kwargs):
        pass

    @abstractmethod
    def create_home_member(self, **kwargs):
        pass

    @abstractmethod
    def get_user_homes(self, user):
        pass