"""Food form serializer module."""
from __future__ import annotations

from typing import Any

from django import forms
from drf_braces import fields
from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field

from nutrition_tracker.forms import FoodForm


class FoodFormSerializer(FormSerializer):
    """Food form serializer class."""

    class Meta:
        form = FoodForm
        field_mapping = {
            forms.UUIDField: make_form_serializer_field(fields.UUIDField),
            forms.FloatField: make_form_serializer_field(fields.FloatField),
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> FoodForm:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
                "lfood": self.context.get("lfood"),
                "food_nutrients": self.context.get("food_nutrients"),
                "food_portions": self.context.get("food_portions"),
            }
        )
        return super().get_form(data=data, **kwargs)
