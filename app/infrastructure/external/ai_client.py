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

    def verify_and_unlock(self, *, smart_lock):
        camera_device = smart_lock.device.paired_camera or smart_lock.device
        stream_url = camera_device.stream_url

        if not stream_url:
            return {"success": False, "authorized": False, "reason": "no_camera_configured"}

        payload = {
            "smart_lock_id": str(smart_lock.id),
            "device_id": str(smart_lock.device.id),
            "home_id": str(smart_lock.device.home.id),
            "stream_url": stream_url,
        }
        try:
            response = requests.post(f"{self.BASE_URL}/smart-lock/verify/", json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "authorized": False, "reason": "ai_engine_error", "error": str(e)}
        
    @staticmethod
    def ask_assistant(home_id: str, question: str) -> dict:
        url = f"{AIClient.BASE_URL}/assistant/query"
        try:
            response = requests.post(
                url,
                json={"home_id": str(home_id), "question": question},
                timeout=500,  # generation can be slow-ish even on gemma3:4b
            )
            if response.status_code >= 400:
                return {"answer": None, "error": response.text}
            return response.json()
        except Exception as e:
            return {"answer": None, "error": str(e)}