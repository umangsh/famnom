"""UserIngredient read view."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin

from nutrition_tracker.views import IngredientMixin, TemplateBaseView


class MyIngredientView(LoginRequiredMixin, IngredientMixin, TemplateBaseView):  # pylint: disable=too-many-ancestors
    """My ingredient view class."""

    template_name: str = "nutrition_tracker/my_food.html"
