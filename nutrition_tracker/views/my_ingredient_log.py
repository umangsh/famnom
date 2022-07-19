"""Log UserIngredient in meals."""
from __future__ import annotations

from nutrition_tracker.forms import LogForm
from nutrition_tracker.views import IngredientMixin, LogFormBaseView, NeverCacheMixin


class MyIngredientLogView(NeverCacheMixin, IngredientMixin, LogFormBaseView):
    """Log UserIngredient class."""

    form_class = LogForm
    template_name: str = "nutrition_tracker/my_food_log.html"
