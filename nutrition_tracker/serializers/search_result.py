"""Search Result serializer module."""
from __future__ import annotations

from rest_framework import serializers

from nutrition_tracker.models import search_result


class SearchResultSerializer(serializers.ModelSerializer):
    """Search Result Serializer class."""

    dname = serializers.ReadOnlyField(source="display_name")
    url = serializers.ReadOnlyField()

    class Meta:
        model = search_result.SearchResult
        fields = (
            "external_id",
            "dname",
            "url",
            "brand_name",
            "brand_owner",
        )
