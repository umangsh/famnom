"""DBFood serializer module."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from django.http import HttpRequest
from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient, food_portion
from nutrition_tracker.models import DBFood, user_ingredient
from nutrition_tracker.serializers import base, db_branded_food


class DBFoodSerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """DBFood Serializer class."""

    brand = db_branded_food.DBBrandedFoodSerializer(source="dbbrandedfood", required=False)
    portions = serializers.SerializerMethodField()
    nutrients = serializers.SerializerMethodField()
    lfood_external_id = serializers.SerializerMethodField()

    non_null_fields = ["brand", "portions", "nutrients", "lfood_external_id"]

    class Meta:
        model = DBFood
        fields = (
            "external_id",
            "description",
            "brand",
            "portions",
            "nutrients",
            "lfood_external_id",
        )

    def get_lfood_external_id(self, obj: DBFood) -> UUID | None:
        """Get LFood external ID for this user and dbfood if it exists."""
        request: HttpRequest | None = self.context.get("request")
        if not request:
            return None

        if not request.user:
            return None

        if not request.user.is_authenticated:
            return None

        lfood = user_ingredient.load_lfood(request.user, db_food_id=obj.id)
        if not lfood:
            return None

        return lfood.external_id

    def get_portions(self, obj: DBFood) -> list[dict[str, Any]]:  # pylint: disable=no-self-use
        """Get food portions for this DBFood."""
        display_portions = food_portion.for_display_choices(None, cfood=obj)
        return [
            {
                "external_id": str(choice[0]),
                "name": choice[1],
                "serving_size": choice[2],
                "serving_size_unit": choice[3],
            }
            for choice in display_portions
        ]

    def get_nutrients(self, obj: DBFood) -> dict[str, Any]:  # pylint: disable=no-self-use
        """Get food nutrients for this DBFood."""
        values = []
        food_nutrients = food_nutrient.get_food_nutrients(None, obj)
        for nutrient_id in constants.LABEL_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if nutrient:
                amount = food_nutrient.get_nutrient_amount(food_nutrients, nutrient_id)
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
