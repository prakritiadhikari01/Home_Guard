import uuid
from datetime import datetime

from django.utils import timezone
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound

from app.application.services.tasks.smart_lock_tasks import auto_relock_task, verify_and_unlock_task
from app.domain.services.access_policy import AccessPolicy
from app.domain.value_objects.lock_status import LockStatus
from app.domain.entities.detection_event import DetectionEvent

from app.infrastructure.db.models.smart_lock_model import SmartLock
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.repositories.django_detection_event_repository import DjangoDetectionEventRepository
from app.infrastructure.external.ai_client import AIClient

detection_event_repo = DjangoDetectionEventRepository()


class SmartLockService:
    @staticmethod
    def _get_lock(device):
        smart_lock = (
            SmartLock.objects
            .select_related("device__home", "last_unlocked_by__user")
            .filter(device=device)
            .first()
        )
        if smart_lock is None:
            raise NotFound("Smart lock not found for this device.")
        return smart_lock

    @staticmethod
    def _require_membership(*, acting_user, device):
        membership = HomeMember.objects.filter(home=device.home, user=acting_user).first()
        if not membership:
            raise PermissionDenied("Not a home member")
        return membership

    @staticmethod
    def _log_access_event(*, smart_lock, event_type, person_type, member_id=None, confidence_score=0.0):
        now = datetime.utcnow()
        event = DetectionEvent(
            id=None,
            home_id=smart_lock.device.home_id,
            device_id=smart_lock.device_id,
            track_id=f"lock-{smart_lock.id}-{now.timestamp()}",
            status="CLOSED",
            pipeline_stage="ENRICHED",
            event_type=event_type,            # ACCESS_GRANTED | ACCESS_DENIED | AUTO_LOCKED | MANUAL_LOCKED
            person_type=person_type,          # KNOWN | UNKNOWN
            person_label=None,
            member_id=member_id,
            face_profile_id=None,
            confidence_score=confidence_score,
            camera_location=None,
            image_url=None,
            snapshot_url=None,
            thumbnail_url=None,
            started_at=now,
            last_seen_at=now,
            timestamp=now,
            metadata={},
        )
        detection_event_repo.create(event)

    # ---------- unlock: button press -> "look at camera" ----------

    @staticmethod
    def start_unlock_attempt(*, acting_user, device):
        """Called synchronously from the view. Fast — kicks off Celery, no AI call here."""
        membership = SmartLockService._require_membership(acting_user=acting_user, device=device)

        if not AccessPolicy.can_unlock_door(membership):
            raise PermissionDenied("Not allowed to unlock this door")

        smart_lock = SmartLockService._get_lock(device)

        verification_id = uuid.uuid4()
        smart_lock.status = LockStatus.VERIFYING.value
        smart_lock.current_verification_id = verification_id
        smart_lock.last_access_result = None
        smart_lock.save()

        verify_and_unlock_task.delay(str(smart_lock.id), str(membership.id), str(verification_id))

        return smart_lock, verification_id

    # ---------- unlock: Celery task calls this after AI engine responds ----------

    # app/application/services/smart_lock_service.py
    @staticmethod
    def resolve_unlock_attempt(*, smart_lock_id, membership_id, verification_id):
        smart_lock = SmartLock.objects.select_related("device__home").get(id=smart_lock_id)

        if str(smart_lock.current_verification_id) != str(verification_id):
            return smart_lock

        result = AIClient().verify_and_unlock(smart_lock=smart_lock)
        recognized = bool(result.get("success")) and bool(result.get("authorized"))
        confidence = result.get("confidence") or 0.0
        deny_reason = result.get("reason")  # "no_face" | "low_quality" | "embedding_failed" | "unknown_person" | None

        if recognized:
            member_id = result.get("member_id")
            membership = HomeMember.objects.filter(id=member_id).first() if member_id else HomeMember.objects.get(id=membership_id)

            smart_lock.status = LockStatus.UNLOCKED.value
            smart_lock.last_unlocked_by = membership
            smart_lock.last_unlocked_at = timezone.now()
            smart_lock.last_access_result = "GRANTED"
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock, event_type="ACCESS_GRANTED", person_type="KNOWN",
                member_id=membership.id, confidence_score=confidence,
            )

            auto_relock_task.apply_async(args=[str(smart_lock.id), str(verification_id)], countdown=15)
        else:
            smart_lock.status = LockStatus.LOCKED.value
            smart_lock.last_access_result = "DENIED"
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock, event_type="ACCESS_DENIED", person_type="UNKNOWN",
                confidence_score=confidence,
            )

        return smart_lock

    # ---------- auto re-lock, 15s after a granted unlock ----------

    @staticmethod
    def auto_relock(*, smart_lock_id, verification_id):
        smart_lock = SmartLock.objects.select_related("device__home").get(id=smart_lock_id)

        # Only relock if this is still the same attempt and it's still unlocked
        # (guards against: user manually locked it early, or a newer attempt started)
        if (
            smart_lock.status == LockStatus.UNLOCKED.value
            and str(smart_lock.current_verification_id) == str(verification_id)
        ):
            smart_lock.status = LockStatus.LOCKED.value
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock,
                event_type="AUTO_LOCKED",
                person_type="KNOWN",
            )

        return smart_lock

    # ---------- manual lock ----------

    @staticmethod
    def manual_lock(*, acting_user, device):
        membership = SmartLockService._require_membership(acting_user=acting_user, device=device)

        if not membership.can_control_devices:
            raise PermissionDenied("Not allowed to lock this door")

        smart_lock = SmartLockService._get_lock(device)
        smart_lock.status = LockStatus.LOCKED.value
        # Invalidate any in-flight verification/auto-relock for this lock
        smart_lock.current_verification_id = None
        smart_lock.save()

        SmartLockService._log_access_event(
            smart_lock=smart_lock,
            event_type="MANUAL_LOCKED",
            person_type="KNOWN",
            member_id=membership.id,
        )

        return smart_lock

    # ---------- auto unlock: used by the ambient camera pipeline (EventService), not the button ----------

    @staticmethod
    def auto_unlock(*, member, device):
        smart_lock = SmartLockService._get_lock(device)

        smart_lock.status = LockStatus.UNLOCKED.value
        smart_lock.last_unlocked_by = member
        smart_lock.last_unlocked_at = timezone.now()
        smart_lock.last_access_result = "GRANTED"
        smart_lock.save()

        SmartLockService._log_access_event(
            smart_lock=smart_lock,
            event_type="ACCESS_GRANTED",
            person_type="KNOWN",
            member_id=member.id,
        )

        return smart_lock

    # ---------- read ----------

    @staticmethod
    def get_lock_detail(device):
        smart_lock = (
            SmartLock.objects
            .select_related("last_unlocked_by__user")
            .filter(device=device)
            .first()
        )
        if smart_lock is None:
            raise NotFound("Smart lock not found.")
        return smart_lock