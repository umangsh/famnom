"""Search results API view."""
from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import generics

from nutrition_tracker.logic import search
from nutrition_tracker.models import search_result
from nutrition_tracker.serializers import SearchResultSerializer


class APISearchResults(generics.ListAPIView):
    """Search results REST API response."""

    serializer_class = SearchResultSerializer

    def get_queryset(self) -> QuerySet[search_result.SearchResult]:
        query = self.request.query_params.get("q")
        return search.search(query)
