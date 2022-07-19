"""Log DBFood API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.constants import constants
from nutrition_tracker.models import db_food, user_ingredient
from nutrition_tracker.serializers import LogSerializer


class APILogDBFood(APIView):
    """Log REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        cfood: db_food.DBFood | None = db_food.load_cfood(external_id=kwargs.get("id"))
        if not cfood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(request.user, db_food_id=cfood.id)

        serializer = LogSerializer(
            data=request.data,
            context={
                "user": request.user,
                "external_id": cfood.external_id,
                "cfood": cfood,
                "lobject": lfood,
            },
        )
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Mobile clients can send empty MealType choice, bail out early in that case.
        if serializer.form_instance.cleaned_data["meal_type"] == constants.MealType.__empty__:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)
