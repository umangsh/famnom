"""Log UserRecipe in meals."""
from __future__ import annotations

from nutrition_tracker.forms import LogForm
from nutrition_tracker.views import LogFormBaseView, NeverCacheMixin, RecipeMixin


class MyRecipeLogView(NeverCacheMixin, RecipeMixin, LogFormBaseView):
    """Log UserRecipe class."""

    form_class = LogForm
    template_name: str = "nutrition_tracker/my_recipe_log.html"
