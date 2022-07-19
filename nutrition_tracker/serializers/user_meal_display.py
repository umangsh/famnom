"""UserMeal serializer module."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient
from nutrition_tracker.models import UserMeal
from nutrition_tracker.serializers import base, user_member_ingredient_display, user_member_recipe_display


class UserMealDisplaySerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserMeal Serializer class."""

    display_nutrients = serializers.SerializerMethodField()
    member_ingredients = serializers.SerializerMethodField()
    member_recipes = serializers.SerializerMethodField()

    non_null_fields = [
        "display_nutrients",
    ]

    class Meta:
        model = UserMeal
        fields = (
            "external_id",
            "meal_date",
            "meal_type",
            "display_nutrients",
            "member_ingredients",
            "member_recipes",
        )

    def get_display_nutrients(self, obj: UserMeal) -> dict[str, Any]:
        """Get food nutrients for this UserMeal."""
        request: HttpRequest | None = self.context.get("request")
        if not request:
            return {}

        if not request.user:
            return {}

        if not request.user.is_authenticated:
            return {}

        lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, [obj]))
        lmember_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, [obj]))
        food_nutrients = food_nutrient.get_foods_nutrients(request.user, lfoods)

        values = []
        for nutrient_id in constants.LABEL_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if nutrient:
                amount = food_nutrient.get_nutrient_amount_in_lparents(
                    [obj], food_nutrients, nutrient.id_, member_recipes=lmember_recipes
                )
                values.append(
                    {
                        "id": nutrient.id_,
                        "name": nutrient.display_name,
                        "amount": amount,
                        "unit": food_nutrient.for_display_unit(nutrient.id_),
                    }
                )

        return {"values": values}

    def get_member_ingredients(self, obj: UserMeal) -> list:
        """Get member ingredients for this UserMeal."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_ingredient_id():
                serializer = user_member_ingredient_display.UserMemberIngredientDisplaySerializer(
                    instance=member, context=self.context
                )
                values.append(serializer.data)

        return values

    def get_member_recipes(self, obj: UserMeal) -> list:
        """Get member recipes for this UserMeal."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_recipe_id():
                serializer = user_member_recipe_display.UserMemberRecipeDisplaySerializer(
                    instance=member, context=self.context
                )
                values.append(serializer.data)

        return values
