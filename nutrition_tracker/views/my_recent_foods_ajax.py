"""Ajax view to lookup recent foods consumed containing a particular nutrient."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.utils import views as views_util

MAX_ITEMS: int = 10
MAX_MEALS: int = 10


class MyRecentFoodsAjaxView(TemplateView):
    """My recent foods ajax view class."""

    template_name: str = "nutrition_tracker/my_recent_foods_ajax.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        nutrient_id: int | None = self.kwargs.get("id")
        if not nutrient_id:
            return super().get(*args, **kwargs)

        if self.request.user.is_authenticated:
            self.recent_lfoods = (  # pylint: disable=attribute-defined-outside-init
                food_nutrient.get_recent_foods_for_nutrient(self.request.user, nutrient_id)
            )
        else:
            self.recent_lfoods = []  # pylint: disable=attribute-defined-outside-init

        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        context["recent_lfoods"] = self.recent_lfoods[:MAX_ITEMS]
        return context
