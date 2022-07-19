"""UserMeal mutable serializer module."""
from __future__ import annotations

from rest_framework import serializers

from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import UserMeal
from nutrition_tracker.serializers import base, user_food_membership


class UserMealMutableSerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserMeal Mutable Serializer class. Used for edit flows."""

    member_ingredients = serializers.SerializerMethodField()
    member_recipes = serializers.SerializerMethodField()

    non_null_fields = [
        "member_ingredients",
        "member_recipes",
    ]

    class Meta:
        model = UserMeal
        fields = (
            "external_id",
            "meal_type",
            "meal_date",
            "member_ingredients",
            "member_recipes",
        )

    def get_member_ingredients(self, obj: UserMeal) -> list:
        """Get member ingredients for this UserMeal."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_ingredient_id():
                serializer = user_food_membership.UserFoodMembershipSerializer(instance=member, context=self.context)
                values.append(serializer.data)

        return values

    def get_member_recipes(self, obj: UserMeal) -> list:
        """Get member recipes for this UserMeal."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_recipe_id():
                serializer = user_food_membership.UserFoodMembershipSerializer(instance=member, context=self.context)
                values.append(serializer.data)

        return values
