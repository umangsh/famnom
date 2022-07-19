"""UserMemberIngredient serializer module."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion
from nutrition_tracker.models import UserFoodMembership, user_ingredient
from nutrition_tracker.serializers import base


class UserMemberIngredientDisplaySerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserMealIngredient Serializer class."""

    display_ingredient = serializers.SerializerMethodField()
    display_portion = serializers.SerializerMethodField()
    ingredient_portion_external_id = serializers.SerializerMethodField()

    non_null_fields = [
        "display_ingredient",
        "display_portion",
        "ingredient_portion_external_id",
    ]

    class Meta:
        model = UserFoodMembership
        fields = (
            "external_id",
            "display_ingredient",
            "display_portion",
            "ingredient_portion_external_id",
        )

    def get_display_ingredient(self, obj: UserFoodMembership) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get UserIngredientDisplay for this UserMemberIngredient."""
        # UserIngredientDisplaySerializer causes cyclic import. Return the ingredient response manually.
        lfood: user_ingredient.UserIngredient | None = obj.child
        if lfood:
            display_brand = {}
            for field in constants.BRAND_FIELDS:
                fieldvalue = lfood.display_brand_field(field)
                if fieldvalue:
                    display_brand[field] = fieldvalue

            return {
                "external_id": lfood.external_id,
                "display_name": lfood.display_name,
                "display_brand": display_brand,
            }
        return {}

    def get_display_portion(self, obj: UserFoodMembership) -> dict:  # pylint: disable=no-self-use
        """Get display portion for this member ingredient."""
        portion = obj.portions[0]  # type: ignore
        return {
            "external_id": portion.external_id,
            "name": food_portion.for_display_portion(portion),
            "serving_size": portion.serving_size,
            "serving_size_unit": portion.serving_size_unit,
            "servings_per_container": portion.servings_per_container,
            "quantity": portion.quantity,
        }

    def get_ingredient_portion_external_id(self, obj: UserFoodMembership) -> str | None:
        """Get display portion for this member ingredient."""
        request: HttpRequest | None = self.context.get("request")
        if not request:
            return None

        if not request.user:
            return None

        if not request.user.is_authenticated:
            return None

        lfood = user_ingredient.load_lfood(request.user, id_=obj.child_id)
        lfood_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)  # type: ignore
        portion = food_portion.get_food_member_portion(obj.portions[0], lfood_portions)  # type: ignore
        return str(portion[0][0])
