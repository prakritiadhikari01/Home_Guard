from app.domain.value_objects.role import Role


class AccessPolicy:

    @staticmethod
    def can_manage_members(membership):
        if not membership:
            return False

        return membership.role in [
            Role.OWNER.value,
            Role.ADMIN.value,
        ]

    @staticmethod
    def is_owner(membership):
        if not membership:
            return False

        return membership.role == Role.OWNER.value

    @staticmethod
    def can_control_devices(membership):
        if not membership:
            return False
        return membership.can_control_devices

    @staticmethod
    def can_unlock_door(membership):
        if not membership:
            return False
        return membership.can_unlock_door