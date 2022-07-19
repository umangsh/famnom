"""Log DBFood food in meals."""
from __future__ import annotations

from nutrition_tracker.forms import LogForm
from nutrition_tracker.views import FoodMixin, LogFormBaseView, NeverCacheMixin


class MyFoodLogView(NeverCacheMixin, FoodMixin, LogFormBaseView):
    """Log DBFood food class."""

    form_class = LogForm
    template_name: str = "nutrition_tracker/my_food_log.html"
