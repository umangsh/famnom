"""UserMeal read view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.views import MealMixin, TemplateBaseView


class MyMealView(LoginRequiredMixin, MealMixin, TemplateBaseView):  # pylint: disable=too-many-ancestors
    """My meal view class."""

    template_name: str = "nutrition_tracker/my_meal.html"
