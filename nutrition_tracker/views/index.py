"""Homepage view."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient, user_prefs
from nutrition_tracker.models import user_meal
from nutrition_tracker.utils import model as model_utils
from nutrition_tracker.utils import url_factory


class HomepageView(TemplateView):
    """Homepage view class."""

    template_name: str = "nutrition_tracker/index.html"

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        td_: str | int = self.request.GET.get("td", 0)
        try:
            self.td_ = int(td_)  # pylint: disable=attribute-defined-outside-init
        except ValueError:
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_PARAM_PARSE)
            self.td_ = 0  # pylint: disable=attribute-defined-outside-init

        if not self.request.user.is_authenticated:
            return super().get(*args, **kwargs)

        self.tracker_time = (  # pylint: disable=attribute-defined-outside-init
            timezone.localtime() + timezone.timedelta(days=self.td_)
        )
        lmeals: list[user_meal.UserMeal] = list(
            user_meal.load_lmeals(self.request.user, meal_date=self.tracker_time.date())
        )
        self.lmeals = model_utils.sort_meals(lmeals)  # pylint: disable=attribute-defined-outside-init
        self.lfoods = list(  # pylint: disable=attribute-defined-outside-init
            data_loaders.load_lfoods_for_lparents(self.request.user, self.lmeals)
        )
        self.member_recipes = list(  # pylint: disable=attribute-defined-outside-init
            data_loaders.load_lrecipes_for_lparents(self.request.user, self.lmeals)
        )
        self.food_nutrients = food_nutrient.get_foods_nutrients(  # pylint: disable=attribute-defined-outside-init
            self.request.user, self.lfoods
        )
        self.nutrient_preferences = user_prefs.filter_preferences(  # pylint: disable=attribute-defined-outside-init
            list(user_prefs.load_nutrition_preferences(self.request.user))
        )
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context

        context["lfoods"] = self.lfoods
        context["member_recipes"] = self.member_recipes
        context["lmeals"] = self.lmeals
        context["food_nutrients"] = self.food_nutrients
        context["nutrient_preferences"] = self.nutrient_preferences

        context["tracker_time"] = self.tracker_time
        context["prev_url"] = url_factory.get_url(reverse(constants.URL_HOME), td=(self.td_ - 1))
        context["today_url"] = reverse(constants.URL_HOME)
        context["next_url"] = url_factory.get_url(reverse(constants.URL_HOME), td=(self.td_ + 1))
        return context
