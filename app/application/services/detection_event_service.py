# app/application/services/detection_event_service.py

from django.utils import timezone

from app.infrastructure.db.models.device_model import (
    Device
)

from app.infrastructure.db.models.home_member_model import (
    HomeMember
)

from app.infrastructure.db.models.face_profile_model import (
    FaceProfile
)

from app.infrastructure.db.models.detection_event_model import (
    DetectionEvent
)

from app.application.services.smart_lock_service import (
    SmartLockService
)

from app.application.services.access_log_service import (
    AccessLogService
)


class DetectionEventService:

    @staticmethod
    def process_ai_detection(payload):

        device = Device.objects.get(
            id=payload["device_id"]
        )

        event_type = payload["event_type"]

        confidence_score = payload.get(
            "confidence_score",
            0.0
        )

        matched_member = None
        matched_face = None

        if event_type == "KNOWN_FACE":

            matched_member = (
                HomeMember.objects.get(
                    id=payload["member_id"]
                )
            )

            matched_face = (
                FaceProfile.objects.get(
                    id=payload["face_profile_id"]
                )
            )

        detection_event = (
            DetectionEvent.objects.create(
                home=device.home,
                device=device,
                person_type=(
                    "KNOWN"
                    if event_type == "KNOWN_FACE"
                    else "UNKNOWN"
                ),
                matched_member=matched_member,
                matched_face=matched_face,
                confidence_score=confidence_score,
                timestamp=timezone.now()
            )
        )

        if matched_member:

            SmartLockService.auto_unlock(
                member=matched_member,
                device=device
            )

        AccessLogService.create_ai_log(
            detection_event=detection_event
        )

        return detection_event