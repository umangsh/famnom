"""My Nutrition REST API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.serializers import NutritionSerializer


class APIMyNutrition(APIView):
    """My Nutrition REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NutritionSerializer(
            data=request.data,
            context={
                "user": request.user,
            },
        )
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)
