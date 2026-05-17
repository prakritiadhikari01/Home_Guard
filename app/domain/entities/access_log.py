class AccessLogEntity:

    def __init__(
        self,
        user_id,
        device_id,
        action,
        result,
        message,
    ):
        self.user_id = user_id
        self.device_id = device_id
        self.action = action
        self.result = result
        self.message = message