"""UserRecipe delete view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import UUIDForm
from nutrition_tracker.views import DeleteFormBaseView, RecipeMixin


class MyRecipeDeleteView(LoginRequiredMixin, RecipeMixin, DeleteFormBaseView):
    """My recipe delete view class."""

    form_class = UUIDForm
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_RECIPE_DELETE
    URL_ERROR: str = constants.URL_MY_RECIPES
    URL_SUCCESS: str = constants.URL_MY_RECIPES
