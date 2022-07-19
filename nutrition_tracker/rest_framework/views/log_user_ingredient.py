"""Log UserIngredient API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion
from nutrition_tracker.models import user_food_membership, user_ingredient
from nutrition_tracker.serializers import LogSerializer


class APILogUserIngredient(APIView):
    """Log UserIngredient REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(
            request.user, external_id=kwargs.get("id")
        )
        if not lfood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        context = {
            "user": request.user,
            "external_id": lfood.external_id,
            "lobject": lfood,
            "cfood": lfood.db_food,
        }

        mid = kwargs.get("mid")
        if mid:
            lmembership = user_food_membership.load_lmembership(request.user, external_id=mid)
            if lmembership:
                food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)
                context.update({"food_portions": food_portions, "lmembership": lmembership})

        serializer = LogSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Mobile clients can send empty MealType choice, bail out early in that case.
        if serializer.form_instance.cleaned_data["meal_type"] == constants.MealType.__empty__:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)
