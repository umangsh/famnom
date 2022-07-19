"""Top foods ajax view for a given nutrient."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.utils import views as views_util


class TopFoodsAjaxView(TemplateView):
    """My top foods ajax view class."""

    template_name: str = "nutrition_tracker/top_foods_ajax.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        nutrient_id: int | None = self.kwargs.get("id")
        if not nutrient_id:
            return super().get(*args, **kwargs)

        self.top_cfoods = food_nutrient.get_top_cfoods_for_nutrient(  # pylint: disable=attribute-defined-outside-init
            nutrient_id
        )
        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["top_cfoods"] = self.top_cfoods
        return context
