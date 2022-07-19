"""My recipes API view."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.serializers import BaseSerializer

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_preference, user_recipe
from nutrition_tracker.serializers import UserRecipeDisplaySerializer


class APIMyRecipes(generics.ListAPIView):
    """MyRecipes REST API response."""

    serializer_class = UserRecipeDisplaySerializer

    def get_serializer(self, *args: Any, **kwargs: Any) -> BaseSerializer[Any]:
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        kwargs["fields"] = ["external_id", "name", "recipe_date"]
        return serializer_class(*args, **kwargs)

    def get_queryset(self) -> QuerySet[user_recipe.UserRecipe]:
        if not self.request.user.is_authenticated:
            return user_recipe.empty_qs()

        flag_set = self.request.query_params.get("fs")
        flag_set = flag_set if flag_set in user_preference.get_flag_names() else None

        flag_unset = self.request.query_params.get("fn")
        flag_unset = flag_unset if flag_unset in user_preference.get_flag_names() else None

        page_size = self.request.query_params.get("ps")
        if page_size:
            self.pagination_class.page_size = page_size  # type: ignore

        external_ids: list[UUID] = []
        if flag_set or flag_unset:
            self.pagination_class.page_size = constants.FORM_MAX_UUIDS  # type: ignore
            flags_set: list = [flag_set] if flag_set else []
            flags_unset: list = [flag_unset] if flag_unset else []
            food_preferences: list[user_preference.UserPreference] = list(
                user_prefs.load_food_preferences(self.request.user)
            )
            filtered_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
                food_preferences, flags_set=flags_set, flags_unset=flags_unset
            )
            external_ids = [fp.food_external_id for fp in filtered_preferences if fp.food_external_id]
            if not external_ids:
                return user_recipe.empty_qs()

        query = self.request.query_params.get("q")
        return user_recipe.load_lrecipes_for_browse(
            self.request.user, external_ids=external_ids, query=query, order_by="-recipe_date"
        )
