from django.db.models import Count, Q

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.smart_lock_model import SmartLock
from app.infrastructure.db.models.detection_event_model import DetectionEvent


class DashboardService:

    @staticmethod
    def get_dashboard(home_id):

        home = (
            Home.objects
            .prefetch_related(
                "members__user",
                "devices",
                "events",
            )
            .get(id=home_id)
        )

        return {
            "home": DashboardService.get_home(home),
            "security_mode": home.security_mode,
            "stats": DashboardService.get_stats(home),
            "members": DashboardService.get_members(home),
            "devices": DashboardService.get_devices(home),
            "smart_locks": DashboardService.get_smart_locks(home),
            "recent_events": DashboardService.get_recent_events(home),
        }

    @staticmethod
    def get_home(home):

        return {
            "id": home.id,
            "name": home.name,
            "address": home.address,
            "security_mode": home.security_mode,
        }

    @staticmethod
    def get_stats(home):

        members_count = HomeMember.objects.filter(
            home=home
        ).count()

        unknown_count = DetectionEvent.objects.filter(
            home=home,
            person_type="UNKNOWN",
        ).count()

        alerts_count = DetectionEvent.objects.filter(
            home=home,
            person_type="INTRUDER",
        ).count()

        total_devices = Device.objects.filter(
            home=home
        ).count()

        online_devices = Device.objects.filter(
            home=home,
            status="online",
        ).count()

        return {
            "members": members_count,
            "unknown_detections": unknown_count,
            "alerts": alerts_count,
            "devices_online": online_devices,
            "devices_total": total_devices,
        }

    @staticmethod
    def get_members(home):

        members = (
            HomeMember.objects
            .select_related("user")
            .filter(home=home)
        )

        data = []

        for member in members:

            data.append({
                "id": member.id,
                "name": member.user.full_name,
                "email": member.user.email,
                "role": member.role,
                "joined_at": member.joined_at,
            })

        return data

    @staticmethod
    def get_devices(home):

        devices = Device.objects.filter(
            home=home
        )

        data = []

        for device in devices:

            data.append({
                "id": device.id,
                "name": device.name,
                "type": device.device_type,
                "location": device.location,
                "status": device.status,
                "ip_address": device.ip_address,
                "last_active": device.last_active,
            })

        return data

    @staticmethod
    def get_smart_locks(home):

        locks = (
            SmartLock.objects
            .select_related(
                "device",
                "last_unlocked_by__user",
            )
            .filter(
                device__home=home
            )
        )

        data = []

        for lock in locks:

            unlocked_by = None

            if lock.last_unlocked_by:

                unlocked_by = {
                    "id": lock.last_unlocked_by.id,
                    "name": lock.last_unlocked_by.user.full_name,
                }

            data.append({
                "id": lock.id,
                "device_name": lock.device.name,
                "location": lock.device.location,
                "status": lock.status,
                "last_unlocked_by": unlocked_by,
                "last_unlocked_at": lock.last_unlocked_at,
            })

        return data

    @staticmethod
    def get_recent_events(home):

        events = (
            DetectionEvent.objects
            .select_related(
                "matched_member__user",
                "device",
            )
            .filter(home=home)
            .order_by("-timestamp")[:10]
        )

        data = []

        for event in events:

            person_name = event.person_label

            if event.matched_member:
                person_name = event.matched_member.user.full_name

            data.append({
                "id": event.id,
                "event_type": event.event_type,
                "person_type": event.person_type,
                "person_name": person_name,
                "device": event.device.name,
                "location": event.camera_location,
                "confidence": event.confidence_score,
                "summary": event.event_summary,
                "timestamp": event.timestamp,
                "thumbnail": event.thumbnail_url,
            })

        return data