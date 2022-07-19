"""UserIngredient delete view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import UUIDForm
from nutrition_tracker.views import DeleteFormBaseView, IngredientMixin


class MyFoodDeleteView(LoginRequiredMixin, IngredientMixin, DeleteFormBaseView):
    """My ingredient delete view class."""

    form_class = UUIDForm
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_FOOD_DELETE
    URL_ERROR: str = constants.URL_MY_FOODS
    URL_SUCCESS: str = constants.URL_MY_FOODS
