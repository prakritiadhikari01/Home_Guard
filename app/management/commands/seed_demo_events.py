# app/management/commands/seed_demo_events.py
"""
Acts as a stand-in AI engine: calls the SAME service/orchestrator layer the
real FastAPI engine will call, so this exercises the actual session state
machine, dedup, and alert-evaluation logic — not a fake static array.

Usage:
    python manage.py seed_demo_events --home-id <uuid>

If --home-id is omitted, uses the first Home found. Requires at least one
Device on that home. Uses the first HomeMember found (if any) for the
"recognized" scenario — skips that scenario if none exist.

Run this against a demo/staging DB. It writes real rows.
"""
import random
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.application.services.detection_event_service import DetectionEventService
from app.domain.services.event_orchestrator import EventOrchestrator
from app.infrastructure.db.repositories.django_detection_event_repository import (
    DjangoDetectionEventRepository,
)
from app.infrastructure.db.repositories.django_alert_repository import DjangoAlertRepository
from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.device_model import Device
from app.infrastructure.db.models.home_member_model import HomeMember


class Command(BaseCommand):
    help = "Seed realistic demo detection events by driving the real orchestrator, like the AI engine would."

    def add_arguments(self, parser):
        parser.add_argument("--home-id", type=str, default=None)
        parser.add_argument("--clear", action="store_true", help="Delete existing events/alerts for this home first")

    def handle(self, *args, **options):
        home = self._resolve_home(options["home_id"])
        devices = list(Device.objects.filter(home=home))
        if not devices:
            self.stderr.write(self.style.ERROR(f"No devices found for home {home.id}. Register one first."))
            return

        member = HomeMember.objects.filter(home=home).select_related("user").first()
        face_profile = None
        if member and getattr(member.user, "face_profile", None):
            face_profile = member.user.face_profile

        if options["clear"]:
            from app.infrastructure.db.models.detection_event_model import DetectionEvent as DEM
            from app.infrastructure.db.models.alerts_model import Alert as AM
            AM.objects.filter(home=home).delete()
            DEM.objects.filter(home=home).delete()
            self.stdout.write("Cleared existing events/alerts for this home.")

        repository = DjangoDetectionEventRepository()
        alert_repository = DjangoAlertRepository()
        orchestrator = EventOrchestrator(repository, alert_repository)
        service = DetectionEventService(orchestrator, repository)

        scenarios = self._build_scenarios(home, devices, member, face_profile)

        created = 0
        for scenario in scenarios:
            self._run_scenario(service, scenario)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} demo sessions (with alerts where applicable) for home {home.id}, "
            f"across {len(devices)} real device(s)."
        ))

    def _member_name(self, member) -> str:
        """
        HomeMember has no name field of its own — the display name lives on
        the related User as `full_name`.
        """
        if member is None:
            return "A member"
        user = getattr(member, "user", None)
        if user and getattr(user, "full_name", None):
            return user.full_name
        return "A member"

    def _pick_device(self, devices, keywords: list[str]):
        """
        Finds a real device whose .location or .name matches one of the
        given keywords (e.g. ['front', 'door']). Falls back to a random
        real device if nothing matches — never invents a location.
        """
        for device in devices:
            haystack = f"{device.location} {device.name}".lower()
            if any(kw in haystack for kw in keywords):
                return device
        return random.choice(devices)

    def _resolve_home(self, home_id):
        if home_id:
            return Home.objects.get(id=home_id)
        home = Home.objects.first()
        if home is None:
            raise SystemExit("No Home exists yet — create one first.")
        return home

    def _run_scenario(self, service: DetectionEventService, scenario: dict):
        """
        Drives open -> progress (x1-2) -> close -> enrich through the REAL
        service layer, with backdated timestamps so the timeline looks like
        it happened over the last day rather than all at once right now.
        """
        base_time = timezone.now() - timedelta(minutes=scenario["minutes_ago"])
        track_id = f"demo-{uuid.uuid4().hex[:8]}"

        open_event = service.open({
            "home_id": scenario["home_id"],
            "device_id": scenario["device_id"],
            "track_id": track_id,
            "started_at": base_time,
            "pipeline_stage": "MOTION_DETECTED",
            "event_type": scenario.get("initial_event_type", "MOTION_DETECTED"),
            "person_type": "UNKNOWN",
            "camera_location": scenario["device"].location,
            "confidence_score": 0.3,
        })

        # progress: recognition resolves
        service.progress(open_event.id, {
            "pipeline_stage": scenario.get("resolved_stage", "OBJECT_DETECTED"),
            "event_type": scenario["event_type"],
            "person_type": scenario["person_type"],
            "person_label": scenario.get("person_label"),
            "member_id": scenario.get("member_id"),
            "face_profile_id": scenario.get("face_profile_id"),
            "confidence_score": scenario["confidence_score"],
            "thumbnail_url": scenario.get("thumbnail_url"),
            "last_seen_at": base_time + timedelta(seconds=scenario["duration_seconds"] / 2),
        })

        # close: session ends, alert evaluation runs here
        closed = service.close(open_event.id, {
            "ended_at": base_time + timedelta(seconds=scenario["duration_seconds"]),
        })

        # enrich: Celery summary worker attaches clip/summary
        if closed:
            service.enrich(closed.id, {
                "event_summary": scenario["summary"],
                "thumbnail_url": scenario.get("thumbnail_url"),
                "clip_url": scenario.get("clip_url"),
            })

    def _build_scenarios(self, home, devices, member, face_profile) -> list[dict]:
        common = {"home_id": home.id}
        scenarios = []

        front_device = self._pick_device(devices, ["front", "door", "entry"])
        back_device = self._pick_device(devices, ["back", "yard", "rear"])
        drive_device = self._pick_device(devices, ["drive", "garage", "gate"])
        side_device = self._pick_device(devices, ["side", "path", "alley"])

        if member:
            scenarios.append({
                **common,
                "device": front_device,
                "device_id": front_device.id,
                "minutes_ago": 45,
                "event_type": "PERSON_DETECTED",
                "person_type": "KNOWN",
                "person_label": self._member_name(member),
                "member_id": member.id,
                "face_profile_id": face_profile.id if face_profile else None,
                "thumbnail_url": face_profile.image_url if face_profile else None,
                "confidence_score": 0.97,
                "duration_seconds": 8,
                "summary": f"{self._member_name(member)} approached and entered through {front_device.location}.",
            })

        scenarios += [
            {
                **common,
                "device": back_device, "device_id": back_device.id,
                "minutes_ago": 90,
                "event_type": "PERSON_DETECTED",
                "person_type": "UNKNOWN",
                "confidence_score": 0.55,
                "duration_seconds": 20,
                "summary": f"Unidentified individual walked through {back_device.location}.",
            },
            {
                **common,
                "device": drive_device, "device_id": drive_device.id,
                "minutes_ago": 200,
                "event_type": "VEHICLE_DETECTED",
                "person_type": "VEHICLE",
                "confidence_score": 0.81,
                "duration_seconds": 15,
                "summary": f"Unrecognized vehicle pulled into {drive_device.location} and parked briefly.",
            },
            {
                **common,
                "device": side_device, "device_id": side_device.id,
                "minutes_ago": 260,
                "event_type": "MOTION_DETECTED",
                "person_type": "UNKNOWN",
                "confidence_score": 0.4,
                "duration_seconds": 5,
                "summary": f"Small motion consistent with an animal crossing {side_device.location}.",
            },
            {
                **common,
                "device": back_device, "device_id": back_device.id,
                "minutes_ago": 5,
                "event_type": "PERSON_DETECTED",
                "person_type": "INTRUDER",
                "confidence_score": 0.88,
                "duration_seconds": 720,  # 12 min, also trips LOITERING
                "summary": f"Unrecognized individual lingered near {back_device.location} for an extended period.",
            },
            {
                **common,
                "device": front_device, "device_id": front_device.id,
                "minutes_ago": 300,
                "event_type": "DOOR_UNLOCKED",
                "person_type": "KNOWN" if member else "UNKNOWN",
                "person_label": self._member_name(member) if member else None,
                "member_id": member.id if member else None,
                "confidence_score": 0.99,
                "duration_seconds": 2,
                "summary": f"{front_device.location} unlocked.",
            },
        ]

        # A cluster of unknown visitors on the SAME real front-door camera to
        # demonstrate the REPEATED_UNKNOWN alert (needs >= 3 in the window).
        for i in range(3):
            scenarios.append({
                **common,
                "device": front_device, "device_id": front_device.id,
                "minutes_ago": 10 - i * 3,
                "event_type": "PERSON_DETECTED",
                "person_type": "UNKNOWN",
                "confidence_score": 0.5,
                "duration_seconds": 6,
                "summary": f"Unidentified visitor briefly appeared at {front_device.location}.",
            })

        random.shuffle(scenarios)
        return scenarios