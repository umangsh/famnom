"""Ajax view to lookup food suggestions/recommendations."""
from __future__ import annotations

from itertools import zip_longest
from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_ingredient, user_meal, user_recipe
from nutrition_tracker.utils import views as views_util

MAX_ITEMS: int = 10
MEAL_DAYS: int = 5
TIME_WINDOW_HOURS: int = 2


class MySuggestedFoodsAjaxView(TemplateView):
    """My suggested foods ajax view class."""

    template_name: str = "nutrition_tracker/my_suggested_foods_ajax.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        suggested_lobjects: list[user_ingredient.UserIngredient | user_recipe.UserRecipe] = []
        if self.request.user.is_authenticated:
            lmeals = user_meal.load_lmeals(self.request.user, order_by="-meal_date", num_days=MEAL_DAYS)

            filtered_lmeals = []
            for days in range(1, MEAL_DAYS):
                timestamp = timezone.localtime() - timezone.timedelta(days=days)
                lower_timestamp = timestamp - timezone.timedelta(hours=TIME_WINDOW_HOURS)
                upper_timestamp = timestamp + timezone.timedelta(hours=TIME_WINDOW_HOURS)

                filtered_lmeals.extend(
                    [
                        lmeal
                        for lmeal in lmeals
                        if lower_timestamp < timezone.localtime(lmeal.created_timestamp) < upper_timestamp
                    ]
                )

            suggested_lfoods = list(data_loaders.load_lfoods_for_lparents(self.request.user, filtered_lmeals))
            suggested_lrecipes = list(data_loaders.load_lrecipes_for_lparents(self.request.user, filtered_lmeals))
            suggested_lobjects = [
                item for pair in zip_longest(suggested_lfoods, suggested_lrecipes) for item in pair if item is not None
            ]

        self.suggested_lobjects = suggested_lobjects  # pylint: disable=attribute-defined-outside-init
        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["suggested_lobjects"] = self.suggested_lobjects[:MAX_ITEMS]
        return context
