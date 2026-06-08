from django.utils import timezone

from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.face_profile_model import FaceProfile
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

    DUPLICATE_WINDOW_SECONDS = 30

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

        member_id = payload.get(
            "member_id"
        )

        face_profile_id = payload.get(
            "face_profile_id"
        )

        if member_id:

            try:

                matched_member = (
                    HomeMember.objects.get(
                        id=member_id
                    )
                )

            except HomeMember.DoesNotExist:
                pass

        if face_profile_id:

            try:

                matched_face = (
                    FaceProfile.objects.get(
                        id=face_profile_id
                    )
                )

            except FaceProfile.DoesNotExist:
                pass

        recent_event = (
            DetectionEvent.objects
            .filter(
                device=device,
                person_type=person_type,
                matched_face=matched_face,
            )
            .order_by("-timestamp")
            .first()
        )

        if recent_event:

            seconds_since_last_event = (
                timezone.now()
                - recent_event.timestamp
            ).total_seconds()

            if (
                seconds_since_last_event
                < DetectionEventService.DUPLICATE_WINDOW_SECONDS
            ):
                return recent_event

        detection_event = (
            DetectionEvent.objects.create(
                home=device.home,

                device=device,

                event_type=payload.get(
                    "event_type",
                    "PERSON_DETECTED"
                ),

                person_type=person_type,

                person_label=payload.get(
                    "person_label"
                ),

                matched_member=matched_member,

                matched_face=matched_face,

                confidence_score=confidence_score,

                image_url=payload.get(
                    "image_url"
                ),

                snapshot_url=payload.get(
                    "snapshot_url"
                ),

                camera_location=payload.get(
                    "camera_location",
                    device.location
                ),

                event_summary=payload.get(
                    "event_summary"
                ),

                duration_seconds=payload.get(
                    "duration_seconds",
                    0
                ),

                metadata=payload.get(
                    "metadata",
                    {}
                ),

                timestamp=payload.get(
                    "timestamp",
                    timezone.now()
                ),
            )
        )

        if matched_member:

            try:

                SmartLockService.auto_unlock(
                    member=matched_member,
                    device=device
                )

            except Exception as e:

                print(
                    "Smart lock error:",
                    e
                )

        try:

            AccessLogService.create_ai_log(
                detection_event=detection_event
            )

        except Exception as e:

            print(
                "Access log error:",
                e
            )

        return detection_event