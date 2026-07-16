from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from app.application.services.dashboard_service import DashboardService
from app.interfaces.api.serializers.dashboard_serializer import DashboardSerializer


class DashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, home_id):

        try:

            dashboard = DashboardService.get_dashboard(
                home_id=home_id,
                user=request.user,
            )

        except PermissionError as e:

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DashboardSerializer(dashboard)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )