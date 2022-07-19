"""UUID serializer module."""
from __future__ import annotations

from django import forms
from drf_braces import fields
from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field

from nutrition_tracker.forms import UUIDForm


class UUIDSerializer(FormSerializer):
    """UUID Serializer class."""

    class Meta:
        form = UUIDForm
        field_mapping = {
            forms.UUIDField: make_form_serializer_field(fields.UUIDField),
        }
