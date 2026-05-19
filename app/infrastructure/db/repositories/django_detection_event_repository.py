from app.infrastructure.db.models.detection_event_model import DetectionEvent

class DjangoDetectionEventRepository:
    @staticmethod
    def create_event(**kwargs):
        """
        Create and save a DetectionEvent.
        """
        return DetectionEvent.objects.create(**kwargs)
