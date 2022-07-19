"""My meals API view."""
from __future__ import annotations

from typing import Any, Sequence

from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.serializers import BaseSerializer

from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import UserMealDisplaySerializer
from nutrition_tracker.utils import model as model_utils


class APIMyMeals(generics.ListAPIView):
    """MyMeals REST API response."""

    serializer_class = UserMealDisplaySerializer

    def get_serializer(self, *args: Any, **kwargs: Any) -> BaseSerializer[Any]:
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        kwargs["fields"] = ["external_id", "meal_type", "meal_date"]
        return serializer_class(*args, **kwargs)

    def get_queryset(self) -> QuerySet[user_meal.UserMeal]:
        if not self.request.user.is_authenticated:
            return user_meal.empty_qs()

        return user_meal.load_lmeals(self.request.user, order_by="-meal_date")

    def paginate_queryset(self, queryset: QuerySet[Any] | Sequence[Any]) -> Sequence[Any] | None:
        object_list = super().paginate_queryset(queryset)
        return model_utils.sort_meals(object_list, reverse=True)  # type: ignore
