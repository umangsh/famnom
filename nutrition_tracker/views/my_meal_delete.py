"""UserMeal delete view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import UUIDForm
from nutrition_tracker.views import DeleteFormBaseView, MealMixin


class MyMealDeleteView(LoginRequiredMixin, MealMixin, DeleteFormBaseView):
    """My meal delete view class."""

    form_class = UUIDForm
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_MEAL_DELETE
    URL_ERROR: str = constants.URL_MY_MEALS
    URL_SUCCESS: str = constants.URL_MY_MEALS
