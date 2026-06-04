from app.infrastructure.db.models.access_log_model import (
    AccessLog
)


class AccessLogService:

    @staticmethod
    def create_ai_log(detection_event):

        user = None
        member_name = "Unknown"
        if (
            detection_event.matched_member
            and detection_event.matched_member.user
        ):
            member_name = getattr(
            detection_event.matched_member.user,
            "full_name",
            detection_event.matched_member.user.email
        )
        message = (
            f"Known face detected: {member_name}"
            if detection_event.person_type == "KNOWN"
            else "Unknown person detected"
        )
        return AccessLog.objects.create(
            user=user,
            device=detection_event.device,
            action="face_recognition",
            result=(
                "success"
                if detection_event.person_type == "KNOWN"
                else "failed"
            ),
            confidence_score=detection_event.confidence_score,
            event_type=detection_event.person_type,
            message=message
        )