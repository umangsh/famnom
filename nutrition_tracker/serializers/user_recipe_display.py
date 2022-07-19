"""UserRecipe serializer module."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient, food_portion
from nutrition_tracker.models import UserRecipe, user_food_membership
from nutrition_tracker.serializers import (
    base,
    user_meal_display,
    user_member_ingredient_display,
    user_member_recipe_display,
)


class UserRecipeDisplaySerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserRecipe Serializer class."""

    display_portions = serializers.SerializerMethodField()
    display_nutrients = serializers.SerializerMethodField()
    member_ingredients = serializers.SerializerMethodField()
    member_recipes = serializers.SerializerMethodField()
    display_membership = serializers.SerializerMethodField()

    non_null_fields = [
        "display_portions",
        "display_nutrients",
        "display_membership",
    ]

    class Meta:
        model = UserRecipe
        fields = (
            "external_id",
            "name",
            "recipe_date",
            "display_portions",
            "display_nutrients",
            "member_ingredients",
            "member_recipes",
            "display_membership",
        )

    def get_display_portions(self, obj: UserRecipe) -> list[dict[str, Any]]:  # pylint: disable=no-self-use
        """Get food portions for this UserRecipe."""
        display_portions = food_portion.for_display_choices(obj)
        return [
            {
                "external_id": str(choice[0]),
                "name": choice[1],
                "serving_size": choice[2],
                "serving_size_unit": choice[3],
                "servings_per_container": choice[4],
                "quantity": choice[5],
            }
            for choice in display_portions
        ]

    def get_display_nutrients(self, obj: UserRecipe) -> dict[str, Any]:
        """Get food nutrients for this UserRecipe."""
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

        return {
            "serving_size": constants.PORTION_SIZE,
            "serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            "values": values,
        }

    def get_member_ingredients(self, obj: UserRecipe) -> list:  # pylint: disable=no-self-use
        """Get member ingredients for this UserRecipe."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_ingredient_id():
                serializer = user_member_ingredient_display.UserMemberIngredientDisplaySerializer(
                    instance=member, context=self.context
                )
                values.append(serializer.data)

        return values

    def get_member_recipes(self, obj: UserRecipe) -> list:  # pylint: disable=no-self-use
        """Get member recipes for this UserRecipe."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_recipe_id():
                serializer = user_member_recipe_display.UserMemberRecipeDisplaySerializer(
                    instance=member, context=self.context
                )
                values.append(serializer.data)

        return values

    def get_display_membership(  # pylint: disable=too-many-return-statements
        self, unused_obj: UserRecipe
    ) -> dict[str, Any] | None:
        """Get display membership for this UserRecipe. Membership ID provided through view context."""
        view = self.context.get("view")
        if not view:
            return None

        mid = view.kwargs.get("mid")
        if not mid:
            return None

        request: HttpRequest | None = self.context.get("request")
        if not request:
            return None

        if not request.user:
            return None

        if not request.user.is_authenticated:
            return None

        lmembership = user_food_membership.load_lmembership(request.user, external_id=mid)
        if not lmembership:
            return None

        serializer = user_member_recipe_display.UserMemberRecipeDisplaySerializer(
            instance=lmembership, context=self.context
        )

        response: dict[str, Any] = {}
        response.update(serializer.data)
        if lmembership.parent_type_id == data_loaders.get_content_type_meal_id():
            meal_serializer = user_meal_display.UserMealDisplaySerializer(
                instance=lmembership.parent, fields=["external_id", "meal_date", "meal_type"]
            )
            response.update({"display_meal": meal_serializer.data})

        return response
