"""Delete UserIngredient API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.models import user_food_membership, user_ingredient, user_meal


class APIDeleteUserIngredient(APIView):
    """Delete UserIngredient REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        external_id = kwargs.get("id")
        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(
            request.user, external_id=external_id
        )
        if not lfood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        mid = kwargs.get("mid")
        if mid:
            lmembership = user_food_membership.load_lmembership(request.user, external_id=mid)
            if lmembership:
                old_meal_id: int = lmembership.parent_id
                lmembership.delete()
                old_lmeal = user_meal.load_lmeal(request.user, id_=old_meal_id)
                if old_lmeal and len(old_lmeal.members) == 0:  # type: ignore
                    old_lmeal.delete()
                return Response(status=status.HTTP_200_OK)

        lfood.delete()
        return Response(status=status.HTTP_200_OK)
