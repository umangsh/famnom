"""DBFood details API view."""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from nutrition_tracker.models import db_food
from nutrition_tracker.serializers import DBFoodSerializer


class APIDetailsDBFood(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """DBFood details REST API response."""

    serializer_class = DBFoodSerializer
    lookup_field = "external_id"
    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[db_food.DBFood]:
        """Get view queryset."""
        return db_food.load_cfoods()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        return self.retrieve(request, *args, **kwargs)
