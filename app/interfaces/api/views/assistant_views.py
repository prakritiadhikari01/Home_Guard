from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from app.infrastructure.external.ai_client import AIClient


class AssistantQueryView(APIView):
    """
    POST /api/homes/<uuid:home_id>/assistant/query/   {"question": "..."}

    User-facing. Forwards to the Windows AI engine, which owns the
    Ollama call, and relays the answer straight back.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, home_id):
        question = request.data.get("question")
        if not question:
            return Response({"error": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = AIClient.ask_assistant(home_id, question)
        print(f"[ASSISTANT] engine call failed: {result.get('error')}")
        if not result.get("answer"):
            return Response(
                {"error": result.get("error", "Assistant unavailable")},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"answer": result["answer"]}, status=status.HTTP_200_OK)