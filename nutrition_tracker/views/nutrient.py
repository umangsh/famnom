"""Nutrient pages."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient


class NutrientView(TemplateView):
    """Nutrient view class."""

    template_name = "nutrition_tracker/nutrient.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        nutrient_id: int | None = self.kwargs.get("id")
        if not nutrient_id:
            return super().get(*args, **kwargs)

        self.lnutrient: None | (  # pylint: disable=attribute-defined-outside-init
            usda_config.USDANutrient
        ) = food_nutrient.get_nutrient(nutrient_id)
        if not self.lnutrient:
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_NUTRIENT_NOT_FOUND)
            return redirect(constants.URL_HOME)

        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["lnutrient"] = self.lnutrient
        return context
