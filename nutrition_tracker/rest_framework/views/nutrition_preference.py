"""Nutrition preferences API view."""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_preference
from nutrition_tracker.serializers import UserPreferenceSerializer


class APINutritionPreference(mixins.ListModelMixin, generics.GenericAPIView):
    """Nutrition preferences API. Available to authenticated users only."""

    serializer_class = UserPreferenceSerializer
    # Override default DRF pagination page size set in settings for this view.
    # Returns all nutrition preferences in the response.
    pagination_class = None

    def get_queryset(self) -> QuerySet[user_preference.UserPreference]:
        """Get view queryset."""
        if not self.request.user.is_authenticated:
            return user_preference.empty_qs()

        return user_prefs.load_nutrition_preferences(self.request.user)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        return self.list(request, *args, **kwargs)
