"""UserRecipe read view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.views import RecipeMixin, TemplateBaseView


class MyRecipeView(LoginRequiredMixin, RecipeMixin, TemplateBaseView):  # pylint: disable=too-many-ancestors
    """My recipe view class."""

    template_name: str = "nutrition_tracker/my_recipe.html"
