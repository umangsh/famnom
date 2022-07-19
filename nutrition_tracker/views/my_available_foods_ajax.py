"""Ajax view that returns available foods in a user's kitchen for a given nutrient_id, sorted in descending order by the amount of nutrient."""
from __future__ import annotations

from typing import Any, Sequence

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.models import db_food_nutrient, user_food_nutrient, user_ingredient
from nutrition_tracker.utils import views as views_util

MAX_ITEMS: int = 10


class MyAvailableFoodsAjaxView(TemplateView):
    """My available foods ajax view class."""

    template_name: str = "nutrition_tracker/my_available_foods_ajax.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        nutrient_id: int | None = self.kwargs.get("id")
        if not nutrient_id:
            return super().get(*args, **kwargs)

        lnutrient: usda_config.USDANutrient | None = food_nutrient.get_nutrient(nutrient_id)

        self.available_lfoods: list[  # pylint: disable=attribute-defined-outside-init
            user_ingredient.UserIngredient
        ] = []
        if self.request.user.is_authenticated and lnutrient:
            lfoods: list[user_ingredient.UserIngredient] = list(user_ingredient.load_lfoods(self.request.user))
            lfoods_nutrients: Sequence[
                db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient
            ] = food_nutrient.get_foods_nutrients(self.request.user, lfoods, nutrient_id=nutrient_id)
            lfoods_nutrients = sorted(lfoods_nutrients, key=lambda x: x.amount, reverse=True)  # type: ignore

            for lfn in lfoods_nutrients:
                if not lfn.amount:
                    continue

                if hasattr(lfn, "ingredient"):
                    lfood = next((lfood for lfood in lfoods if lfood == lfn.ingredient), None)  # type: ignore
                else:
                    lfood = next((lfood for lfood in lfoods if lfood.db_food == lfn.db_food), None)  # type: ignore

                if lfood and lfood not in self.available_lfoods:
                    self.available_lfoods.append(lfood)

        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        context["available_lfoods"] = self.available_lfoods[:MAX_ITEMS]
        return context
