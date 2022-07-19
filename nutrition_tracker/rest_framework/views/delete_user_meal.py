"""Delete UserMeal API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.models import user_meal


class APIDeleteUserMeal(APIView):
    """Delete UserMeal REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        external_id = kwargs.get("id")
        lmeal: user_meal.UserMeal | None = user_meal.load_lmeal(request.user, external_id=external_id)
        if not lmeal:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lmeal.delete()
        return Response(status=status.HTTP_200_OK)
