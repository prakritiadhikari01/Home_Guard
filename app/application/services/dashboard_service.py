from django.shortcuts import get_object_or_404
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.detection_event_model import DetectionEvent
from app.domain.value_objects.device_status import DeviceStatus

class DashboardService:

    @classmethod
    def get_dashboard(cls, home_id, user):
        """
        Returns everything required by the dashboard page.
        """

        home = cls._get_home(home_id, user)

        return {
            "home": cls._get_home_information(home),
            "security_mode": cls._get_security_mode(home, user),
            "summary": cls._get_summary(home),
            "stats": cls._get_stats(home),
            "live_preview": cls._get_live_preview(home),
            "recent_events": cls._get_recent_events(home),
        }

    @staticmethod
    def _get_home(home_id, user):
        """
        Validate user belongs to the requested home.
        """

        home = get_object_or_404(
            Home.objects.select_related("owner"),
            id=home_id,
        )

        if home.owner_id == user.id:
            return home

        is_member = HomeMember.objects.filter(
            home=home,
            user=user,
        ).exists()

        if not is_member:
            raise PermissionError(
                "You are not a member of this home."
            )

        return home

    @staticmethod
    def _get_home_information(home):

        return {
            "id": home.id,
            "name": home.name,
        }

    @staticmethod
    def _get_security_mode(home, user):

        return {
            "current": home.security_mode,
            "can_change": home.owner_id == user.id,
        }

    @staticmethod
    def _get_summary(home):

        alerts = DetectionEvent.objects.filter(
            home=home,
            person_type="INTRUDER",
        ).count()

        unknown = DetectionEvent.objects.filter(
            home=home,
            person_type="UNKNOWN",
        ).count()

        if alerts > 0:
            message = (
                f"{alerts} active alert(s) require immediate attention."
            )

        elif unknown > 0:
            message = (
                f"{unknown} unknown visitor(s) detected recently."
            )

        else:
            message = (
                "Everything looks secure. No unusual activity detected."
            )

        return {
            "title": "AI Intelligence Brief",
            "message": message,
        }

    @staticmethod
    def _get_stats(home):

        members = HomeMember.objects.filter(
            home=home,
        ).count()

        unknown = DetectionEvent.objects.filter(
            home=home,
            person_type="UNKNOWN",
        ).count()

        alerts = DetectionEvent.objects.filter(
            home=home,
            person_type="INTRUDER",
        ).count()

        devices_total = Device.objects.filter(
            home=home,
        ).count()

        devices_online = Device.objects.filter(
            home=home,
            status=DeviceStatus.ONLINE.value,
        ).count()

        return {
            "members": members,
            "unknown_detections": unknown,
            "alerts": alerts,
            "devices_online": devices_online,
            "devices_total": devices_total,
        }

    @staticmethod
    def _get_live_preview(home):
        """
        Dashboard shows only first four cameras.
        """

        devices = (
            Device.objects.filter(
                home=home,
            )
            .order_by("name")[:4]
        )

        previews = []

        for device in devices:

            latest_event = (
                DetectionEvent.objects.filter(
                    device=device,
                )
                .order_by("-timestamp")
                .first()
            )

            previews.append(
                {
                    "id": device.id,
                    "name": device.name,
                    "location": device.location,
                    "status": device.status,
                    "stream_url": device.stream_url,
                    "current_detection": (
                        latest_event.person_label
                        if latest_event
                        else "No Activity"
                    ),
                }
            )

        return previews

    @staticmethod
    def _get_recent_events(home):

        events = (
            DetectionEvent.objects.filter(
                home=home,
            )
            .select_related(
                "device",
                "matched_member__user",
            )
            .order_by("-timestamp")[:5]
        )

        results = []

        for event in events:

            if event.matched_member:
                summary = (
                    f"{event.matched_member.user.full_name} "
                    f"detected at {event.device.location}"
                )

            else:
                summary = event.event_summary

            results.append(
                {
                    "id": event.id,
                    "summary": summary,
                    "device": event.device.name,
                    "timestamp": event.timestamp,
                }
            )

        return results

    @staticmethod
    def _get_summary(home):
        return {
            "title": "Ask Me Anything",
            "message": "Curious about today's activity? Ask about any visitor, event, or camera — I'll pull the answer from your home's activity.",
        }

    
        