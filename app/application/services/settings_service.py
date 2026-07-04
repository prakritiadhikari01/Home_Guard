from app.infrastructure.db.models.home_settings_model import HomeSettings
from app.infrastructure.db.models.user_settings_model import UserSettings
from app.infrastructure.db.models.device_settings_model import DeviceSettings
from app.infrastructure.db.models.home_member_model import HomeMember


class SettingsService:

    @staticmethod
    def get_settings(user, home_id):
        """
        Returns all settings for the selected home.
        """

        membership = HomeMember.objects.select_related("home").get(
            user=user,
            home_id=home_id,
        )

        home = membership.home

        home_settings = HomeSettings.objects.get(home=home)

        user_settings = UserSettings.objects.get(user=user)

        device_settings = DeviceSettings.objects.filter(
            device__home=home
        ).select_related("device")

        return {
            "home_settings": home_settings,
            "user_settings": user_settings,
            "device_settings": device_settings,
        }

    @staticmethod
    def update_home_settings(home_settings, data):

        for field, value in data.items():
            setattr(home_settings, field, value)

        home_settings.save()

        return home_settings

    @staticmethod
    def update_user_settings(user_settings, data):

        for field, value in data.items():
            setattr(user_settings, field, value)

        user_settings.save()

        return user_settings

    @staticmethod
    def update_device_settings(device_settings, data):

        for field, value in data.items():
            setattr(device_settings, field, value)

        device_settings.save()

        return device_settings