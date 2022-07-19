"""UserRecipe mutable serializer module."""
from __future__ import annotations

from rest_framework import serializers

from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import UserRecipe
from nutrition_tracker.serializers import base, user_food_membership, user_food_portion


class UserRecipeMutableSerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserRecipe Mutable Serializer class. Used for edit flows."""

    portions = user_food_portion.UserFoodPortionSerializer(many=True, required=False)
    member_ingredients = serializers.SerializerMethodField()
    member_recipes = serializers.SerializerMethodField()

    non_null_fields = [
        "portions",
        "member_ingredients",
        "member_recipes",
    ]

    class Meta:
        model = UserRecipe
        fields = (
            "external_id",
            "name",
            "recipe_date",
            "portions",
            "member_ingredients",
            "member_recipes",
        )

    def get_member_ingredients(self, obj: UserRecipe) -> list:
        """Get member ingredients for this UserRecipe."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_ingredient_id():
                serializer = user_food_membership.UserFoodMembershipSerializer(instance=member, context=self.context)
                values.append(serializer.data)

        return values

    def get_member_recipes(self, obj: UserRecipe) -> list:
        """Get member recipes for this UserRecipe."""
        values = []
        for member in obj.members:  # type: ignore
            if member.child_type_id == data_loaders.get_content_type_recipe_id():
                serializer = user_food_membership.UserFoodMembershipSerializer(instance=member, context=self.context)
                values.append(serializer.data)

        return values
