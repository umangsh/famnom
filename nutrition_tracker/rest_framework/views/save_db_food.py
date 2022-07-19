"""Save DBFood API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.models import db_food, user_ingredient
from nutrition_tracker.serializers import UUIDSerializer


class APISaveDBFood(APIView):
    """Save DBFood REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = UUIDSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        external_id = serializer.validated_data["id"]
        cfood: db_food.DBFood | None = db_food.load_cfood(external_id=external_id)
        if not cfood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(request.user, db_food_id=cfood.id)
        if not lfood:
            user_ingredient.create(luser=request.user, db_food=cfood)

        return Response(status=status.HTTP_200_OK)
