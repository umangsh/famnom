"""DBFood read view."""
from __future__ import annotations

from nutrition_tracker.views import FoodMixin, TemplateBaseView


class MyFoodView(FoodMixin, TemplateBaseView):
    """My food view class."""

    template_name: str = "nutrition_tracker/my_food.html"
