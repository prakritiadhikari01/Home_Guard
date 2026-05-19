import requests

from decouple import config


class AIClient:
    """
    Client to communicate with the Windows AI service.
    """

    BASE_URL = config("AI_SERVICE_URL")

    @staticmethod
    def analyze_frame(image_base64):
        """
        Send image frame to AI service.
        """

        url = f"{AIClient.BASE_URL}/analyze"

        try:
            response = requests.post(
                url,
                json={
                    "image": image_base64
                },
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException:
            return {
                "face_match": None,
                "confidence": 0.0,
                "type": "UNKNOWN"
            }