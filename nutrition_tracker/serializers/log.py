"""UUID serializer module."""
from __future__ import annotations

from typing import Any

from django import forms
from drf_braces import fields
from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field

from nutrition_tracker.forms import LogForm


class LogSerializer(FormSerializer):
    """Log food/recipe Serializer class."""

    class Meta:
        form = LogForm
        field_mapping = {
            forms.UUIDField: make_form_serializer_field(fields.UUIDField),
            forms.FloatField: make_form_serializer_field(fields.FloatField),
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> LogForm:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "external_id": self.context.get("external_id"),
                "user": self.context.get("user"),
                "lobject": self.context.get("lobject"),
                "cfood": self.context.get("cfood"),
                "lmeal": self.context.get("lmeal"),
                "lmembership": self.context.get("lmembership"),
                "food_portions": self.context.get("food_portions"),
            }
        )
        return super().get_form(data=data, **kwargs)
