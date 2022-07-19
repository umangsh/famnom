"""UserMeal details API view."""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import UserMealDisplaySerializer


class APIDetailsUserMeal(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """UserMeal details REST API response."""

    serializer_class = UserMealDisplaySerializer
    lookup_field = "external_id"
    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[user_meal.UserMeal]:
        """Get view queryset."""
        if not self.request.user.is_authenticated:
            return user_meal.empty_qs()

        return user_meal.load_lmeals(self.request.user)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        return self.retrieve(request, *args, **kwargs)
