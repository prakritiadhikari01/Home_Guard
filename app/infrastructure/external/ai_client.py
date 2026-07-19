# app/infrastructure/external/ai_client.py
import requests
from django.conf import settings

from app.infrastructure.db.models.home_member_model import HomeMember
from app.infrastructure.db.models.smart_lock_model import SmartLock


class AIClient:
    """
    Client to communicate with Windows AI Engine
    """

    BASE_URL = settings.AI_SERVICE_URL
    TIMEOUT = settings.AI_TIMEOUT

    # Camera registration and management endpoints (for future use)
    @staticmethod
    def register_camera(payload):
        url = f"{AIClient.BASE_URL}/camera/register"

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=AIClient.TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    # FACE REGISTRATION
    @staticmethod
    def register_face(payload):
        url = f"{AIClient.BASE_URL}/face/register"

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=AIClient.TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    # FRAME ANALYSIS (YOUR EXISTING)
    @staticmethod
    def analyze_frame(image_base64):
        url = f"{AIClient.BASE_URL}/analyze"

        try:
            response = requests.post(
                url,
                json={"image": image_base64},
                timeout=AIClient.TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            return {
                "face_match": None,
                "confidence": 0.0,
                "type": "UNKNOWN"
            }

    # EMBEDDING EXTRACTION
    @staticmethod
    def extract_embedding(image_base64):
        url = f"{AIClient.BASE_URL}/extract-embedding"

        try:
            response = requests.post(
                url,
                json={"image": image_base64},
                timeout=AIClient.TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            return {
                "success": False,
                "embedding": None
            }

    def verify_and_unlock(
        self,
        *,
        smart_lock,
    ):
        payload = {
            "smart_lock_id": str(smart_lock.id),
            "device_id": str(smart_lock.device.id),
            "home_id": str(smart_lock.device.home.id),
            "stream_url": smart_lock.device.stream_url,
        }

        response = requests.post(
            f"{self.BASE_URL}/smart-lock/verify/",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()
   
    @staticmethod
    def manual_unlock(*, acting_user, device):

        membership = HomeMember.objects.filter(
            home=device.home,
            user=acting_user,
        ).first()

        if not membership:
            raise ("Not a home member")

        smart_lock = SmartLock.objects.get(device=device)

        result = AIClient().verify_and_unlock(
            smart_lock=smart_lock,
        )

        return result