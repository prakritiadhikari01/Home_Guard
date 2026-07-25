# app/application/services/smart_lock_service.py
import uuid

from django.utils import timezone
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound

from app.domain.services.access_policy import AccessPolicy
from app.domain.value_objects.lock_status import LockStatus
from app.domain.value_objects.event_type import EventType
from app.domain.value_objects.person_type import PersonType
from app.domain.value_objects.events import EventStatus, PipelineStage

from app.infrastructure.db.models.smart_lock_model import SmartLock
from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.detection_event_model import DetectionEvent
from app.infrastructure.external.ai_client import AIClient


class SmartLockService:

    # ---------- internal helpers ----------

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
        """Gates who can trigger a scan on this home's camera — NOT the
        unlock decision itself. The unlock decision is made later,
        against whoever the camera actually recognizes."""
        membership = HomeMember.objects.filter(home=device.home, user=acting_user).first()
        if not membership:
            raise PermissionDenied("Not a home member")
        return membership

    @staticmethod
    def _log_access_event(*, smart_lock, event_type, person_type, member=None, member_id =None,
                           face_profile_id=None, person_label=None, confidence=0.0, reason=None):
        now = timezone.now()
        person_label = None
        if member_id:
            membership = HomeMember.objects.filter(id=member_id).select_related("user").first()
            if membership:
                person_label = membership.user.full_name

        DetectionEvent.objects.create(
            home=smart_lock.device.home,
            device=smart_lock.device,
            track_id=f"lock-{smart_lock.id}-{now.timestamp()}",
            status=EventStatus.CLOSED.value,
            pipeline_stage=PipelineStage.FACE_RECOGNIZED.value,
            event_type=event_type,            # EventType.DOOR_UNLOCKED / DOOR_LOCKED / ACCESS_DENIED
            person_type=person_type,          # PersonType.KNOWN / PersonType.UNKNOWN
            person_label=person_label,
            matched_member=member,
            matched_face_id=face_profile_id,
            confidence_score=confidence,
            camera_location=getattr(smart_lock.device, "camera_location", None),
            started_at=now,
            last_seen_at=now,
            ended_at=now,
            duration_seconds=0,
            timestamp=now,
            metadata={"reason": reason} if reason else {},
        )

    # ---------- unlock: button press -> "look at camera" ----------

    @staticmethod
    def request_unlock(*, acting_user, device):
        SmartLockService._require_membership(acting_user=acting_user, device=device)

        smart_lock = SmartLockService._get_lock(device)

        verification_id = uuid.uuid4()
        smart_lock.status = LockStatus.VERIFYING.value
        smart_lock.current_verification_id = verification_id
        smart_lock.last_access_result = None
        smart_lock.save()

        from app.application.services.tasks.smart_lock_tasks import verify_and_unlock_task
        verify_and_unlock_task.delay(str(smart_lock.id), str(verification_id))

        return smart_lock, verification_id

    # ---------- Celery task calls this once the AI engine responds ----------

    @staticmethod
    def resolve_unlock_attempt(*, smart_lock_id, verification_id):
        smart_lock = SmartLock.objects.select_related("device__home").get(id=smart_lock_id)

        if str(smart_lock.current_verification_id) != str(verification_id):
            return smart_lock  # a newer attempt has already replaced this one

        result = AIClient().verify_and_unlock(smart_lock=smart_lock)
        recognized = bool(result.get("success")) and result.get("person_type") == "KNOWN"
        confidence = result.get("confidence") or 0.0
        person_label = result.get("person_label")
        face_profile_id = result.get("face_profile_id")
        reason = result.get("reason")

        membership = (
            HomeMember.objects.filter(id=result.get("member_id")).first()
            if recognized else None
        )
        granted = bool(membership) and AccessPolicy.can_unlock_door(membership)

        if granted:
            smart_lock.status = LockStatus.UNLOCKED.value
            smart_lock.last_unlocked_by = membership
            smart_lock.last_unlocked_at = timezone.now()
            smart_lock.last_access_result = "GRANTED"
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock, event_type=EventType.DOOR_UNLOCKED.value,
                person_type=PersonType.KNOWN.value, member=membership,
                face_profile_id=face_profile_id, person_label=person_label, confidence=confidence,
            )
            from app.application.services.tasks.smart_lock_tasks import auto_relock_task
            auto_relock_task.apply_async(args=[str(smart_lock.id), str(verification_id)], countdown=50)
        else:
            smart_lock.status = LockStatus.LOCKED.value
            smart_lock.last_access_result = "DENIED"
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock, event_type=EventType.ACCESS_DENIED.value,
                person_type=PersonType.KNOWN.value if recognized else PersonType.UNKNOWN.value,
                member=membership, face_profile_id=face_profile_id, person_label=person_label,
                confidence=confidence,
                reason=reason if not recognized else "not_authorized",
            )

        return smart_lock

    # ---------- auto re-lock, 15s after a granted unlock ----------

    @staticmethod
    def auto_relock(*, smart_lock_id, verification_id):
        smart_lock = SmartLock.objects.select_related("device__home").get(id=smart_lock_id)

        if (
            smart_lock.status == LockStatus.UNLOCKED.value
            and str(smart_lock.current_verification_id) == str(verification_id)
        ):
            smart_lock.status = LockStatus.LOCKED.value
            smart_lock.save()

            SmartLockService._log_access_event(
                smart_lock=smart_lock, event_type=EventType.DOOR_LOCKED.value,
                person_type=PersonType.KNOWN.value, member=smart_lock.last_unlocked_by,
                reason="auto_relock",
            )

        return smart_lock

    # ---------- manual lock (physical/app lock, not face-gated) ----------

    @staticmethod
    def manual_lock(*, acting_user, device):
        membership = SmartLockService._require_membership(acting_user=acting_user, device=device)

        if not membership.can_control_devices:
            raise PermissionDenied("Not allowed to lock this door")

        smart_lock = SmartLockService._get_lock(device)
        smart_lock.status = LockStatus.LOCKED.value
        smart_lock.current_verification_id = None
        smart_lock.last_access_result = None
        smart_lock.save()

        SmartLockService._log_access_event(
            smart_lock=smart_lock, event_type=EventType.DOOR_LOCKED.value,
            person_type=PersonType.KNOWN.value, member=membership, confidence=1.0,
            reason="manual_lock",
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