"""Nutrition API view. Returns nutrition label/form metadata."""
from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.serializers import NutritionSerializer


class APINutritionLabel(APIView):
    """Nutrition API. Available to authenticated users only."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        return Response({"results": NutritionSerializer.get_label_nutrients()})
