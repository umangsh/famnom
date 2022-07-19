"""UserMemberRecipe serializer module."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.logic import food_portion
from nutrition_tracker.models import UserFoodMembership, user_recipe
from nutrition_tracker.serializers import base


class UserMemberRecipeDisplaySerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserMemberRecipe Serializer class."""

    display_recipe = serializers.SerializerMethodField()
    display_portion = serializers.SerializerMethodField()
    recipe_portion_external_id = serializers.SerializerMethodField()

    non_null_fields = [
        "display_recipe",
        "display_portion",
        "recipe_portion_external_id",
    ]

    class Meta:
        model = UserFoodMembership
        fields = (
            "external_id",
            "display_recipe",
            "display_portion",
            "recipe_portion_external_id",
        )

    def get_display_recipe(self, obj: UserFoodMembership) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get UserRecipeDisplay for this UserMemberRecipe."""
        # UserRecipeDisplaySerializer causes cyclic import. Return the recipe response manually.
        lrecipe: user_recipe.UserRecipe | None = obj.child
        if lrecipe:
            return {
                "external_id": lrecipe.external_id,
                "name": lrecipe.name,
                "recipe_date": lrecipe.recipe_date,
            }
        return {}

    def get_display_portion(self, obj: UserFoodMembership) -> dict:  # pylint: disable=no-self-use
        """Get display portion for this member recipe."""
        portion = obj.portions[0]  # type: ignore
        return {
            "external_id": portion.external_id,
            "name": food_portion.for_display_portion(portion),
            "serving_size": portion.serving_size,
            "serving_size_unit": portion.serving_size_unit,
            "servings_per_container": portion.servings_per_container,
            "quantity": portion.quantity,
        }

    def get_recipe_portion_external_id(self, obj: UserFoodMembership) -> str | None:  # pylint: disable=no-self-use
        """Get display portion for this member ingredient."""
        request: HttpRequest | None = self.context.get("request")
        if not request:
            return None

        if not request.user:
            return None

        if not request.user.is_authenticated:
            return None

        lrecipe = user_recipe.load_lrecipe(request.user, id_=obj.child_id)
        lrecipe_portions = food_portion.for_display_choices(lrecipe)
        portion = food_portion.get_food_member_portion(obj.portions[0], lrecipe_portions)  # type: ignore
        return str(portion[0][0])
