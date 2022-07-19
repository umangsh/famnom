"""Nutrient page details API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.logic import food_nutrient, user_prefs
from nutrition_tracker.serializers import DBFoodSerializer, UserIngredientDisplaySerializer

DEFAULT_CHART_DAYS = 5


class APINutrient(APIView):
    """Nutrient page details REST API Response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # pylint: disable=too-many-locals
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        nutrient_id = self.kwargs.get("id")
        if not nutrient_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lnutrient = food_nutrient.get_nutrient(nutrient_id)
        if not lnutrient:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = {}

        # Metadata fields
        nutrient_metadata = {
            "id": lnutrient.id_,
            "name": lnutrient.display_name,
            "unit": food_nutrient.for_display_unit(lnutrient.id_),
            "description": lnutrient.description,
            "wikipedia_url": lnutrient.wikipedia_url,
        }
        response.update(nutrient_metadata)

        # Recent foods
        lfoods = food_nutrient.get_recent_foods_for_nutrient(request.user, nutrient_id)
        serializer = UserIngredientDisplaySerializer(
            instance=lfoods, many=True, fields=["external_id", "display_name", "display_brand"]
        )
        response.update({"recent_lfoods": serializer.data})

        # Top cfoods
        cfoods = food_nutrient.get_top_cfoods_for_nutrient(nutrient_id)
        db_serializer = DBFoodSerializer(instance=cfoods, many=True, fields=["external_id", "description", "brand"])
        response.update({"top_cfoods": db_serializer.data})

        # Tracker data
        nutrient_preferences = user_prefs.filter_preferences(list(user_prefs.load_nutrition_preferences(request.user)))
        nutrient_preference = user_prefs.filter_preferences_by_id(nutrient_preferences, food_nutrient_id=nutrient_id)

        if nutrient_preference:
            nutrient_threshold = user_prefs.get_threshold_value(nutrient_preference)
        else:
            nutrient_threshold = None

        tracker_window = self.kwargs.get("days", DEFAULT_CHART_DAYS)  # days
        date_to_nutrient_map = food_nutrient.get_tracker_nutrients(
            request.user, nutrient_id, total_days=tracker_window
        )
        date_str_to_nutrient_map = {}
        for date, value in date_to_nutrient_map.items():
            date_str_to_nutrient_map[date.strftime("%Y-%m-%d")] = value
        response.update({"threshold": nutrient_threshold, "amount_per_day": date_str_to_nutrient_map})
        return Response(response, status=status.HTTP_200_OK)
