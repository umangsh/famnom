"""Daily tracker API view."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient
from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import UserMealDisplaySerializer
from nutrition_tracker.utils import model as model_utils


class APITracker(APIView):
    """Tracker details REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # pylint: disable=too-many-locals
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        tracker_date = self.kwargs.get("td")
        try:
            tracker_datetime = datetime.strptime(tracker_date, "%Y-%m-%d")
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response: dict[str, Any] = {}
        lmeals = list(user_meal.load_lmeals(request.user, meal_date=tracker_datetime))
        lmeals = model_utils.sort_meals(lmeals)
        lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, lmeals))
        lmember_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, lmeals))
        food_nutrients = food_nutrient.get_foods_nutrients(request.user, lfoods)

        display_meals = [
            UserMealDisplaySerializer(
                instance=lmeal,
                fields=["external_id", "meal_date", "meal_type", "member_ingredients", "member_recipes"],
            )
            for lmeal in lmeals
        ]
        response.update({"display_meals": [item.data for item in display_meals]})

        values = []
        for nutrient_id in constants.TRACKER_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if nutrient:
                amount = food_nutrient.get_nutrient_amount_in_lparents(
                    lmeals, food_nutrients, nutrient.id_, member_recipes=lmember_recipes
                )
                values.append(
                    {
                        "id": nutrient.id_,
                        "name": nutrient.display_name,
                        "amount": amount,
                        "unit": food_nutrient.for_display_unit(nutrient.id_),
                    }
                )

        response.update({"display_nutrients": {"values": values}})
        return Response(response, status=status.HTTP_200_OK)
