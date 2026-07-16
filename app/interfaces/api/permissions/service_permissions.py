from rest_framework.permissions import BasePermission
from django.conf import settings


class IsAIEngine(BasePermission):
    """
    Machine-to-machine auth for the FastAPI AI engine (Windows).
    The AI engine has no user account, so JWT doesn't apply here —
    it authenticates with a shared secret sent as X-API-Key.
    """

    def has_permission(self, request, view):
        expected_key = getattr(settings, "AI_ENGINE_API_KEY", None)
        provided_key = request.headers.get("X-API-Key")

        if not expected_key:
            # Misconfigured server — fail closed, not open.
            return False

        return provided_key == expected_key