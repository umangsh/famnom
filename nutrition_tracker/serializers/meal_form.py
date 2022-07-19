"""Meal form serializer module."""
from __future__ import annotations

from typing import Any

from django import forms
from drf_braces import fields
from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field

from nutrition_tracker.forms import MealForm


class MealFormSerializer(FormSerializer):
    """Meal form serializer class."""

    class Meta:
        form = MealForm
        field_mapping = {
            forms.UUIDField: make_form_serializer_field(fields.UUIDField),
            forms.FloatField: make_form_serializer_field(fields.FloatField),
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> MealForm:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
                "lmeal": self.context.get("lmeal"),
            }
        )
        return super().get_form(data=data, **kwargs)
