"""Search view."""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import search
from nutrition_tracker.models import SearchResult
from nutrition_tracker.serializers import SearchResultSerializer
from nutrition_tracker.utils import views as views_util
from nutrition_tracker.views import ListBaseView


class SearchResultsView(ListBaseView):  # pylint: disable=too-many-ancestors
    """Search view class - HTTP and AJAX."""

    context_object_name: str = "search_results"
    model = SearchResult
    template_name: str = "nutrition_tracker/search.html"
    URL_INVALID_SEARCH: str = constants.URL_SEARCH
    rawsearch: bool = False

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.request.GET.get("format") == "json" or views_util.is_ajax(self.request):
            self.paginate_by = constants.AUTOCOMPLETE_PAGE_SIZE
            self.rawsearch = True

        return super().get(self, *args, **kwargs)

    def get_queryset(self) -> QuerySet[SearchResult]:
        return search.search(self.query, raw=self.rawsearch)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.GET.get("format") == "json" or views_util.is_ajax(self.request):
            # Use rest framework serializers. Shared with the API.
            data = SearchResultSerializer(context[self.context_object_name], many=True)
            return HttpResponse(JSONRenderer().render(data.data), "application/json")

        return super().render_to_response(context, **response_kwargs)
