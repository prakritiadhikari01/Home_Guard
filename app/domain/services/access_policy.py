from app.domain.value_objects.role import Role


class AccessPolicy:

    @staticmethod
    def can_manage_members(member):
        return member.role in [Role.OWNER.value, Role.ADMIN.value]

    @staticmethod
    def can_control_devices(member):
        return member.can_control_devices

    @staticmethod
    def can_unlock_door(member):
        return member.can_unlock_door