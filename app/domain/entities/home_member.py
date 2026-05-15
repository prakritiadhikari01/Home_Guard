class HomeMemberEntity:
    def __init__(
        self,
        home_id,
        user_id,
        role,
        can_view_dashboard=True,
        can_control_devices=False,
        can_manage_members=False,
        can_unlock_door=False,
        receive_alerts=True,
    ):
        self.home_id = home_id
        self.user_id = user_id
        self.role = role
        self.can_view_dashboard = can_view_dashboard
        self.can_control_devices = can_control_devices
        self.can_manage_members = can_manage_members
        self.can_unlock_door = can_unlock_door
        self.receive_alerts = receive_alerts