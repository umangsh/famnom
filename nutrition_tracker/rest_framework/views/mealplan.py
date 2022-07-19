"""Mealplan REST API views."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.logic import mealplan, user_prefs
from nutrition_tracker.models import user_ingredient, user_preference, user_recipe
from nutrition_tracker.serializers import (
    MealplanFormOneSerializer,
    MealplanFormThreeSerializer,
    MealplanFormTwoSerializer,
    UserIngredientDisplaySerializer,
    UserPreferenceSerializer,
    UserRecipeDisplaySerializer,
)


class APIMealplanFormOne(APIView):
    """Mealplan Form One REST API response."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = MealplanFormOneSerializer(
            data=request.data,
            context={
                "user": request.user,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)


class APIMealplanFormTwo(APIView):
    """Mealplan Form Two REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # pylint: disable=too-many-locals
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        food_preferences = list(user_prefs.load_food_preferences(request.user))
        usable_preferences = user_prefs.filter_preferences(
            food_preferences, flags_set_any=[user_preference.FLAG_IS_AVAILABLE, user_preference.FLAG_IS_NOT_ZEROABLE]
        )
        items = {fp.food_external_id: fp for fp in usable_preferences if fp.food_external_id}

        values = []
        lfoods = list(user_ingredient.load_lfoods(request.user, external_ids=list(items.keys())))
        for lfood in lfoods:
            food_serializer = UserIngredientDisplaySerializer(instance=lfood, fields=["external_id", "display_name"])
            preference_serializer = UserPreferenceSerializer(instance=items[lfood.external_id], fields=["thresholds"])
            value: dict = {}
            value.update(food_serializer.data)
            # Rename 'display_name' to 'name'.
            value["name"] = value["display_name"]
            del value["display_name"]
            value.update(preference_serializer.data)
            values.append(value)

        lrecipes = list(user_recipe.load_lrecipes(request.user, external_ids=list(items.keys())))
        for lrecipe in lrecipes:
            recipe_serializer = UserRecipeDisplaySerializer(instance=lrecipe, fields=["external_id", "name"])
            preference_serializer = UserPreferenceSerializer(
                instance=items[lrecipe.external_id], fields=["thresholds"]
            )
            value = {}
            value.update(recipe_serializer.data)
            value.update(preference_serializer.data)
            values.append(value)

        return Response(values, status.HTTP_200_OK)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = MealplanFormTwoSerializer(
            data=request.data,
            context={
                "user": request.user,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)


class APIMealplanFormThree(APIView):
    """Mealplan Form Three REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        lmealplan = mealplan.get_mealplan_for_user(request.user)
        values = {"infeasible": lmealplan.infeasible, "results": []}
        for lfood in lmealplan.lfoods:
            quantity = lmealplan.quantity_map.get(lfood.external_id)
            if not quantity:
                continue

            food_serializer = UserIngredientDisplaySerializer(instance=lfood, fields=["external_id", "display_name"])
            value: dict = {}
            value.update(food_serializer.data)
            # Rename 'display_name' to 'name'.
            value["name"] = value["display_name"]
            del value["display_name"]
            value.update({"quantity": quantity})
            values["results"].append(value)  # type: ignore

        for lrecipe in lmealplan.lrecipes:
            quantity = lmealplan.quantity_map.get(lrecipe.external_id)
            if not quantity:
                continue

            recipe_serializer = UserRecipeDisplaySerializer(instance=lrecipe, fields=["external_id", "name"])
            value = {}
            value.update(recipe_serializer.data)
            value.update({"quantity": quantity})
            values["results"].append(value)  # type: ignore

        return Response(values, status.HTTP_200_OK)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = MealplanFormThreeSerializer(
            data=request.data,
            context={
                "user": request.user,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # The rendered mealplan is gone once computed.
        # serializer.form_instance doesn't have
        # serializer.form_instance.data set.
        # Explicitly set it to request.data here.
        serializer.form_instance.data = request.data
        serializer.form_instance.save()
        return Response(status=status.HTTP_200_OK)
