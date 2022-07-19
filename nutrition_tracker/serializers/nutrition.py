"""Nutrition form and FDA RDIs serializer module."""
from __future__ import annotations

from typing import Any

from django import forms
from drf_braces import fields
from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field

from nutrition_tracker.config import nutrition as nutrition_config
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import NutritionForm
from nutrition_tracker.logic import food_nutrient


class NutritionSerializer(FormSerializer):
    """Nutrition form and FDA RDIs serializer class."""

    class Meta:
        form = NutritionForm
        field_mapping = {
            forms.FloatField: make_form_serializer_field(fields.FloatField),
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> NutritionForm:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
            }
        )
        return super().get_form(data=data, **kwargs)

    @classmethod
    def get_label_nutrients(cls) -> list[dict]:
        """Return label nutrients metadata as a map."""
        values = []
        for nutrient_id in constants.LABEL_NUTRIENT_IDS:
            nutrient = food_nutrient.get_nutrient(nutrient_id)
            if not nutrient:
                continue

            values.append(
                {
                    "id": nutrient_id,
                    "name": nutrient.display_name,
                    "unit": food_nutrient.for_display_unit(nutrient_id),
                }
            )

        return values

    @classmethod
    def get_fda_rdi(cls) -> dict:
        """Return FDA nutrition RDIs as a map."""
        serialized: dict = {
            constants.FDA_ADULT: {},
            constants.FDA_INFANT: {},
            constants.FDA_CHILDREN: {},
            constants.FDA_PREGNANT: {},
        }

        for rdi in nutrition_config.fda_nutrient_rdis:
            nutrient = food_nutrient.get_nutrient(rdi.nutrient_id)
            if not nutrient:
                continue

            serialized[constants.FDA_ADULT][rdi.nutrient_id] = {
                "value": rdi.adult,
                "threshold": rdi.threshold and rdi.threshold.value,
                "name": nutrient.display_name,
                "unit": food_nutrient.for_display_unit(rdi.nutrient_id),
            }

            serialized[constants.FDA_INFANT][rdi.nutrient_id] = {
                "value": rdi.infant,
                "threshold": rdi.threshold and rdi.threshold.value,
                "name": nutrient.display_name,
                "unit": food_nutrient.for_display_unit(rdi.nutrient_id),
            }

            serialized[constants.FDA_CHILDREN][rdi.nutrient_id] = {
                "value": rdi.children,
                "threshold": rdi.threshold and rdi.threshold.value,
                "name": nutrient.display_name,
                "unit": food_nutrient.for_display_unit(rdi.nutrient_id),
            }

            serialized[constants.FDA_PREGNANT][rdi.nutrient_id] = {
                "value": rdi.pregnant,
                "threshold": rdi.threshold and rdi.threshold.value,
                "name": nutrient.display_name,
                "unit": food_nutrient.for_display_unit(rdi.nutrient_id),
            }

        return serialized
