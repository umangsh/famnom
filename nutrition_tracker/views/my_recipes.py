"""UserRecipe browse view."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_preference, user_recipe
from nutrition_tracker.views import ListBaseView, RecipeMixin


class MyRecipesView(LoginRequiredMixin, RecipeMixin, ListBaseView):  # pylint: disable=too-many-ancestors
    """My recipes view class."""

    context_object_name: str = "lrecipes"
    model = user_recipe.UserRecipe
    template_name: str = "nutrition_tracker/my_recipes.html"

    def get_queryset(self) -> QuerySet[user_recipe.UserRecipe]:
        luser: user_model.User = self.request.user  # type: ignore
        external_ids: list[UUID] = []
        if self.flag_set or self.flag_unset:
            self.paginate_by: int = constants.FORM_MAX_UUIDS
            flags_set: list = [self.flag_set] if self.flag_set else []
            flags_unset: list = [self.flag_unset] if self.flag_unset else []
            food_preferences: list[user_preference.UserPreference] = list(user_prefs.load_food_preferences(luser))
            filtered_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
                food_preferences, flags_set=flags_set, flags_unset=flags_unset
            )
            external_ids = [fp.food_external_id for fp in filtered_preferences if fp.food_external_id]
            if not external_ids:
                return user_recipe.empty_qs()

        return user_recipe.load_lrecipes_for_browse(
            luser, external_ids=external_ids, query=self.query, order_by="-recipe_date"
        )

    def get_results(self, context: dict[str, Any]) -> list:
        """Return recipe browse results."""
        return [
            {
                "id": str(lrecipe.external_id),
                "text": lrecipe.display_name(with_date=True),
            }
            for lrecipe in context[self.context_object_name]
        ]
