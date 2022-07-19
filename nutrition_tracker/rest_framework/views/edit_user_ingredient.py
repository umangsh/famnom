"""Edit User Ingredient REST API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.forms import FoodPortionFormset
from nutrition_tracker.logic import food_nutrient, food_portion
from nutrition_tracker.models import user_ingredient
from nutrition_tracker.serializers import FoodFormSerializer, UserIngredientMutableSerializer


class APIEditUserIngredient(APIView):
    """Edit User Ingredient REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        external_id = self.kwargs.get("id")
        if not external_id:
            # Create flow
            return Response(status=status.HTTP_200_OK)

        lfood = user_ingredient.load_lfood(request.user, external_id=external_id)
        if not lfood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = UserIngredientMutableSerializer(instance=lfood)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        lfood = user_ingredient.load_lfood(request.user, external_id=request.data.get("external_id"))

        if lfood:
            food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
            food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)
        else:
            food_nutrients = []
            food_portions = []

        serializer = FoodFormSerializer(
            data=request.data,
            context={
                "user": request.user,
                "lfood": lfood,
                "food_nutrients": food_nutrients,
                "food_portions": food_portions,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        servings = FoodPortionFormset(request.data, instance=lfood)
        if not servings.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfood = serializer.form_instance.save(servings)
        if lfood:
            return Response(lfood.external_id, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
