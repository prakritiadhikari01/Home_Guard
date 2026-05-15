from enum import Enum


class Role(Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"
    SECURITY = "SECURITY"

    @classmethod
    def choices(cls):
        return [(role.value, role.value) for role in cls]