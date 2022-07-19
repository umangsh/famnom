"""UserIngredient details API view."""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from nutrition_tracker.models import user_ingredient
from nutrition_tracker.serializers import UserIngredientDisplaySerializer


class APIDetailsUserIngredient(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """UserIngredient details REST API response."""

    serializer_class = UserIngredientDisplaySerializer
    lookup_field = "external_id"
    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[user_ingredient.UserIngredient]:
        """Get view queryset."""
        if not self.request.user.is_authenticated:
            return user_ingredient.empty_qs()

        return user_ingredient.load_lfoods(self.request.user)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        return self.retrieve(request, *args, **kwargs)
