from app.domain.services.event_orchestrator import EventOrchestrator
from app.domain.entities.detection_event import DetectionEvent


class DetectionEventService:
    def __init__(self, orchestrator: EventOrchestrator):
        self.orchestrator = orchestrator

    def ingest(self, validated_data: dict) -> DetectionEvent:
        incoming = DetectionEvent(
            id=None,
            home_id=validated_data["home_id"],
            device_id=validated_data["device_id"],
            event_type=validated_data["event_type"],
            person_type=validated_data["person_type"],
            person_label=validated_data.get("person_label"),
            member_id=validated_data.get("member_id"),
            face_profile_id=validated_data.get("face_profile_id"),
            confidence_score=validated_data.get("confidence_score", 0.0),
            camera_location=validated_data.get("camera_location"),
            image_url=validated_data.get("image_url"),
            snapshot_url=validated_data.get("snapshot_url"),
            timestamp=validated_data["timestamp"],
            duration_seconds=0,
            metadata={},
        )
        return self.orchestrator.process_detection(incoming)