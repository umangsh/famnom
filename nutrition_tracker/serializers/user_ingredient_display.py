"""UserIngredient serializer module."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_category, food_nutrient, food_portion
from nutrition_tracker.models import UserIngredient, user_food_membership
from nutrition_tracker.serializers import base, user_meal_display, user_member_ingredient_display


class UserIngredientDisplaySerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserIngredient Serializer class."""

    display_name = serializers.SerializerMethodField()
    display_brand = serializers.SerializerMethodField()
    display_portions = serializers.SerializerMethodField()
    display_nutrients = serializers.SerializerMethodField()
    display_category = serializers.SerializerMethodField()
    display_membership = serializers.SerializerMethodField()

    non_null_fields = [
        "display_name",
        "display_brand",
        "display_portions",
        "display_nutrients",
        "display_category",
        "display_membership",
    ]

    class Meta:
        model = UserIngredient
        fields = (
            "external_id",
            "display_name",
            "display_brand",
            "display_portions",
            "display_nutrients",
            "display_category",
            "display_membership",
        )

    def get_display_name(self, obj: UserIngredient) -> str | None:  # pylint: disable=no-self-use
        """Get display name for this UserIngredient."""
        return obj.display_name

    def get_display_brand(self, obj: UserIngredient) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get brand information for this UserIngredient."""
        response = {}
        for field in constants.BRAND_FIELDS:
            fieldvalue = obj.display_brand_field(field)
            if fieldvalue:
                response[field] = fieldvalue

        return response

    def get_display_portions(self, obj: UserIngredient) -> list[dict[str, Any]]:  # pylint: disable=no-self-use
        """Get food portions for this UserIngredient."""
        display_portions = food_portion.for_display_choices(obj, cfood=obj.db_food)
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

    def get_display_nutrients(self, obj: UserIngredient) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get food nutrients for this UserIngredient."""
        values = []
        food_nutrients = food_nutrient.get_food_nutrients(obj, cfood=obj.db_food)
        for nutrient_id in constants.LABEL_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if nutrient:
                amount = food_nutrient.get_nutrient_amount(food_nutrients, nutrient.id_)
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

    def get_display_category(self, obj: UserIngredient) -> str | None:  # pylint: disable=no-self-use
        """Get food display category for this UserIngredient."""
        if obj.category_id:
            return food_category.for_display(obj.category_id)

        if obj.db_food and obj.db_food.food_category_id:
            return food_category.for_display(obj.db_food.food_category_id)

        return None

    def get_display_membership(  # pylint: disable=too-many-return-statements
        self, unused_obj: UserIngredient
    ) -> dict[str, Any] | None:
        """Get display membership for this UserIngredient. Membership ID provided through view context."""
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

        serializer = user_member_ingredient_display.UserMemberIngredientDisplaySerializer(
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
