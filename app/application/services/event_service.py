from django.shortcuts import get_object_or_404
from django.conf import settings
from app.infrastructure.db.repositories.django_detection_event_repository import DjangoDetectionEventRepository
from app.infrastructure.db.repositories.django_home_member_repository import DjangoHomeMemberRepository
from app.infrastructure.db.repositories.django_smart_lock_repository import DjangoSmartLockRepository
from app.infrastructure.db.repositories.django_access_log_repository import DjangoAccessLogRepository
from app.infrastructure.external.ai_client import AIClient
from app.application.services.smart_lock_service import SmartLockService
from app.infrastructure.db.models.home_member_model import HomeMember

class EventService:
    detection_event_repo = DjangoDetectionEventRepository()
    home_member_repo = DjangoHomeMemberRepository()
    smart_lock_repo = DjangoSmartLockRepository()
    access_log_repo = DjangoAccessLogRepository()

    @staticmethod
    def process_event(home, device, image_base64, event_timestamp):
        """
        Orchestrates AI analysis and access decision for an incoming event.
        """
        # Call the Windows AI service
        ai_result = AIClient.analyze_frame(image_base64)
        face_match = ai_result.get("face_match")
        person_type = ai_result.get("type", "UNKNOWN")
        confidence = ai_result.get("confidence", 0.0)

        matched_user = None
        membership = None

        # If AI returned a face_match (expected to be a user ID), get that user and membership
        if face_match is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                matched_user = User.objects.get(id=face_match)
                membership = EventService.home_member_repo.get_membership(home, matched_user)
            except User.DoesNotExist:
                matched_user = None
                membership = None

        # Attempt to unlock if recognized and authorized
        unlocked = False
        if matched_user and membership:
            try:
                # Find the smart lock in this home (assumes one lock per home; adjust logic if multiple)
                smart_lock = EventService.smart_lock_repo.get_lock_by_id(device.id)
                # If device is not a lock itself, find any lock for the home
                if not smart_lock:
                    smart_lock = EventService.smart_lock_repo.get_lock_by_id(
                        list(home.devices.filter(device_type="smart_lock").values_list('id', flat=True)).first()
                    )
                if smart_lock:
                    # Try unlocking door
                    SmartLockService.unlock_door(acting_user=matched_user, home=home, smart_lock=smart_lock)
                    unlocked = True
            except Exception:
                unlocked = False  # PermissionDenied or other; SmartLockService has already logged it

        # Determine final event type
        if matched_user:
            if unlocked:
                event_type = "ACCESS_GRANTED"
            else:
                event_type = "ACCESS_DENIED"
        else:
            event_type = "INTRUDER_DETECTED"

        # Create and save the DetectionEvent
        EventService.detection_event_repo.create_event(
            home=home,
            device=device,
            person_type=person_type,
            matched_user=matched_user,
            confidence_score=confidence,
            timestamp=event_timestamp
        )
