from django.utils import timezone

from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.detection_event_model import DetectionEvent

from app.application.services.smart_lock_service import SmartLockService
from app.application.services.access_log_service import AccessLogService


class DetectionEventService:

    @staticmethod
    def process_ai_detection(payload):

        device = Device.objects.get(
            id=payload["device_id"]
        )

        person_type = payload.get(
            "person_type",
            "UNKNOWN"
        )

        confidence_score = payload.get(
            "confidence_score",
            0.0
        )

        matched_member = None
        matched_face = None

        member_id = payload.get("member_id")
        face_profile_id = payload.get("face_profile_id")

        if member_id:
            try:
                matched_member = HomeMember.objects.get(
                    id=member_id
                )
            except HomeMember.DoesNotExist:
                pass

        if face_profile_id:
            try:
                matched_face = FaceProfile.objects.get(
                    id=face_profile_id
                )
            except FaceProfile.DoesNotExist:
                pass

        detection_event = DetectionEvent.objects.create(
            home=device.home,
            device=device,
            person_type=person_type,
            matched_member=matched_member,
            matched_face=matched_face,
            confidence_score=confidence_score,
            image_url=payload.get("image_url"),
            timestamp=payload.get(
                "timestamp",
                timezone.now()
            ),
            camera_location=device.location,
        )

        if matched_member:
            try:
                SmartLockService.auto_unlock(
                    member=matched_member,
                    device=device
                )
            except Exception:
                pass

        try:
            AccessLogService.create_ai_log(
                detection_event=detection_event
            )
        except Exception:
            pass

        return detection_event