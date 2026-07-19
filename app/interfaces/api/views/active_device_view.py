# app/interfaces/api/views/active_device_view.py
#
# EXTENDED VERSION — adds nested `settings` and the parent home's
# `security_mode` to each camera, so the AI Engine's RuntimeManager can
# build a full execution plan (device settings + house security mode)
# from ONE call instead of N+1 requests per camera.
#
# Everything else (permission classes, base filter) is unchanged from
# your original file. Drop this in to replace it.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from app.infrastructure.db.models.device_model import Device
from app.domain.value_objects.device_type import DeviceType
from app.domain.value_objects.device_status import DeviceStatus


class ActiveDeviceListView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        cameras = (
            Device.objects.filter(
                device_type=DeviceType.CAMERA.value,
                status=DeviceStatus.ONLINE.value,
            )
            .select_related("home", "home__settings", "settings")
        )

        data = []
        for camera in cameras:
            device_settings = getattr(camera, "settings", None)
            home_settings = getattr(camera.home, "settings", None)

            data.append(
                {
                    "id": str(camera.id),
                    "name": camera.name,
                    "home_id": str(camera.home.id),
                    "location": camera.location,
                    "stream_url": camera.stream_url,
                    "status": camera.status,
                    "device_type": camera.device_type,
                    "security_mode": camera.home.security_mode,
                    "settings": (
                        {
                            "enabled": device_settings.enabled,
                            "motion_detection": device_settings.motion_detection,
                            "human_detection": device_settings.human_detection,
                            "face_recognition": device_settings.face_recognition,
                            "animal_detection": device_settings.animal_detection,
                            "vehicle_detection": device_settings.vehicle_detection,
                            "package_detection": device_settings.package_detection,
                            "recording_enabled": device_settings.recording_enabled,
                            "snapshot_enabled": device_settings.snapshot_enabled,
                            "confidence_threshold": device_settings.confidence_threshold,
                        }
                        if device_settings
                        else {}
                    ),
                    "home_settings": (
                        {
                            "timeline_enabled": home_settings.timeline_enabled,
                            "log_known_member_entry": home_settings.log_known_member_entry,
                            "log_unknown_person": home_settings.log_unknown_person,
                            "notify_unknown_person": home_settings.notify_unknown_person,
                            "notify_family_members": home_settings.notify_family_members,
                            "emergency_contact_enabled": home_settings.emergency_contact_enabled,
                            "escalate_repeated_detection": home_settings.escalate_repeated_detection,
                            "ai_summary_enabled": home_settings.ai_summary_enabled,
                            "clip_recording_enabled": home_settings.clip_recording_enabled,
                            "snapshot_enabled": home_settings.snapshot_enabled,
                            "ignore_animals": home_settings.ignore_animals,
                            "loitering_seconds": home_settings.loitering_seconds,
                            "repeated_detection_window": home_settings.repeated_detection_window,
                        }
                        if home_settings
                        else {}
                    ),
                }
            )

        return Response({"count": len(data), "cameras": data})