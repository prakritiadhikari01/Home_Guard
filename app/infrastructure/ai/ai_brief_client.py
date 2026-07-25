import requests
from django.conf import settings


class AIBriefClient:
    @classmethod
    def get_brief(cls, home_id: str) -> dict:
        try:
            response = requests.post(
                f"{settings.AI_SERVICE_URL}/brief",
                json={"home_id": home_id},
                timeout=8,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[AIBriefClient] error: {e}")
            return {
                "title": "Brief unavailable",
                "message": "We couldn't generate today's summary right now.",
            }