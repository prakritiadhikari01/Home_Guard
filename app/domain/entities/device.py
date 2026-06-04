# app/domain/entities/device.py
class DeviceEntity:

    def __init__(
        self,
        home_id,
        name,
        device_type,
        ip_address,
        location,
    ):
        self.home_id = home_id
        self.name = name
        self.device_type = device_type
        self.ip_address = ip_address
        self.location = location