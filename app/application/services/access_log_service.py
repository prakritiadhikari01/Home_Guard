# app/application/services/access_log_service.py

from app.infrastructure.db.models.access_log_model import (
    AccessLog
)


class AccessLogService:

    @staticmethod
    def create_ai_log(detection_event):

        AccessLog.objects.create(
            user=(
                detection_event.matched_member.user
                if detection_event.matched_member
                else None
            ),
            device=detection_event.device,
            action="face_recognition",
            result=(
                "success"
                if detection_event.person_type == "KNOWN"
                else "failed"
            ),
            confidence_score=(
                detection_event.confidence_score
            ),
            event_type=detection_event.person_type,
            message=(
                "Known face detected"
                if detection_event.person_type == "KNOWN"
                else "Unknown person detected"
            )
        )