"""Base serializer module."""
from __future__ import annotations

from contextlib import suppress
from typing import Any, Mapping

from rest_framework import serializers


class NonNullModelSerializer(serializers.ModelSerializer):
    """Filters our null values in response."""

    non_null_fields: list[str] = []

    def to_representation(self, instance: object) -> Mapping[str, Any]:
        rep = super().to_representation(instance)
        for field in self.non_null_fields:
            with suppress(KeyError):
                if rep[field] is None:
                    rep.pop(field)
        return rep


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
