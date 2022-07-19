"""Ajax view to lookup nutrient information for a food/recipe."""
from __future__ import annotations

from typing import Any, Sequence

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient
from nutrition_tracker.models import db_food_nutrient, user_food_nutrient, user_ingredient, user_recipe
from nutrition_tracker.utils import views as views_util


class MyNutrientAjaxView(LoginRequiredMixin, TemplateView):
    """My nutrient ajax view class."""

    @method_decorator(views_util.ajax_login_required)
    def get(self, *args: Any, **kwargs: Any) -> HttpResponse | JsonResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        luser: user_model.User = self.request.user  # type: ignore
        external_id: str | None = kwargs.get("id")
        if not external_id:
            return JsonResponse({})

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(luser, external_id=external_id)
        if lfood:
            food_nutrients: Sequence[
                db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient
            ] = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
            data: list = [
                {
                    "nutrient_id": nutrient_id,
                    "amount": food_nutrient.get_nutrient_amount(food_nutrients, nutrient_id),
                }
                for nutrient_id in constants.LABEL_NUTRIENT_IDS
            ]
        else:
            lrecipe: user_recipe.UserRecipe | None = user_recipe.load_lrecipe(luser, external_id=external_id)
            if lrecipe:
                lfoods: list[user_ingredient.UserIngredient] = list(
                    data_loaders.load_lfoods_for_lparents(luser, [lrecipe])
                )
                lrecipes: list[user_recipe.UserRecipe] = list(
                    data_loaders.load_lrecipes_for_lparents(luser, [lrecipe])
                )
                food_nutrients = food_nutrient.get_foods_nutrients(luser, lfoods)
                data = [
                    {
                        "nutrient_id": nutrient_id,
                        "amount": food_nutrient.get_nutrient_amount_in_lparents(
                            [lrecipe], food_nutrients, nutrient_id, member_recipes=lrecipes
                        ),
                    }
                    for nutrient_id in constants.LABEL_NUTRIENT_IDS
                ]
            else:
                return JsonResponse({})

        return JsonResponse(data, safe=False)
