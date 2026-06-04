# app/infrastructure/external/ai_client.py
import requests
from django.conf import settings


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