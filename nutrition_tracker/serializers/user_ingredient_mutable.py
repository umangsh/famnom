"""UserIngredient mutable serializer module."""
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_category, food_nutrient, food_portion
from nutrition_tracker.models import UserIngredient
from nutrition_tracker.serializers import base, user_food_portion


class UserIngredientMutableSerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """UserIngredient Mutable Serializer class. Used for edit flows."""

    name = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    portions = user_food_portion.UserFoodPortionSerializer(many=True, required=False)
    nutrients = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    non_null_fields = [
        "name",
        "brand",
        "portions",
        "nutrients",
        "category",
    ]

    class Meta:
        model = UserIngredient
        fields = (
            "external_id",
            "name",
            "brand",
            "portions",
            "nutrients",
            "category",
        )

    def get_name(self, obj: UserIngredient) -> str | None:  # pylint: disable=no-self-use
        """Get name for this UserIngredient."""
        return obj.display_name

    def get_brand(self, obj: UserIngredient) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get brand information for this UserIngredient."""
        response = {}
        for field in constants.BRAND_FIELDS:
            fieldvalue = obj.display_brand_field(field)
            if fieldvalue:
                response[field] = fieldvalue

        return response

    def get_nutrients(self, obj: UserIngredient) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get food nutrients for this UserIngredient."""
        values = []
        food_portions = food_portion.for_display_choices(obj, cfood=obj.db_food)

        serving_size: float = constants.PORTION_SIZE
        serving_size_unit: str = str(constants.ServingSizeUnit.WEIGHT)
        if food_portions and food_portions[0][2]:
            serving_size = food_portions[0][2]
            if food_portions[0][3]:
                serving_size_unit = food_portions[0][3]

        food_nutrients = food_nutrient.get_food_nutrients(obj, cfood=obj.db_food)
        for nutrient_id in constants.FORM_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if nutrient:
                amount = food_nutrient.get_nutrient_amount(food_nutrients, nutrient.id_)
                amount = (
                    round(amount * serving_size / constants.PORTION_SIZE, constants.RW_FLOAT_PRECISION)
                    if amount
                    else amount
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
            "serving_size": serving_size,
            "serving_size_unit": serving_size_unit,
            "values": values,
        }

    def get_category(self, obj: UserIngredient) -> str | None:  # pylint: disable=no-self-use
        """Get food display category for this UserIngredient."""
        if obj.category_id:
            return food_category.for_display(obj.category_id)

        if obj.db_food and obj.db_food.food_category_id:
            return food_category.for_display(obj.db_food.food_category_id)

        return None
