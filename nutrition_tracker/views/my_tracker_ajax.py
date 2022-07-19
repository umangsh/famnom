"""Ajax view to lookup nutrient consumption over time."""
from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient, user_prefs
from nutrition_tracker.utils import views as views_util

TRACKER_WINDOW: int = 30  # days


class MyTrackerAjaxView(TemplateView):
    """My tracker ajax view class."""

    template_name: str = "nutrition_tracker/my_tracker_ajax.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        nutrient_id: int | None = self.kwargs.get("id")
        if not nutrient_id:
            return super().get(*args, **kwargs)

        self.lnutrient: None | (  # pylint: disable=attribute-defined-outside-init
            usda_config.USDANutrient
        ) = food_nutrient.get_nutrient(nutrient_id)

        self.nutrients_per_day: list[dict] = []  # pylint: disable=attribute-defined-outside-init
        self.thresholds_per_day: list[dict] = []  # pylint: disable=attribute-defined-outside-init
        nutrient_threshold: float | None = None
        if self.request.user.is_authenticated and self.lnutrient:
            nutrient_preferences = user_prefs.filter_preferences(
                list(user_prefs.load_nutrition_preferences(self.request.user))
            )
            nutrient_preference = user_prefs.filter_preferences_by_id(
                nutrient_preferences, food_nutrient_id=nutrient_id
            )

            if nutrient_preference:
                nutrient_threshold = user_prefs.get_threshold_value(nutrient_preference)
            else:
                nutrient_threshold = None

            date_to_nutrient_map = food_nutrient.get_tracker_nutrients(
                self.request.user, nutrient_id, total_days=TRACKER_WINDOW
            )

            for days in range(TRACKER_WINDOW):
                current_date = timezone.localdate() - timezone.timedelta(days=days)
                self.nutrients_per_day.append({"x": str(current_date), "y": date_to_nutrient_map[current_date]})
                self.thresholds_per_day.append({"x": str(current_date), "y": nutrient_threshold})

        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        context["lnutrient"] = self.lnutrient
        context["nutrients_per_day"] = json.dumps(self.nutrients_per_day)
        context["nutrient_thresholds"] = json.dumps(self.thresholds_per_day)
        context["days_window_size"] = TRACKER_WINDOW
        return context
