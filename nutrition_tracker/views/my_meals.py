"""UserMeal browse view."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.models import user_meal
from nutrition_tracker.utils import model as model_utils
from nutrition_tracker.views import ListBaseView, MealMixin


class MyMealsView(LoginRequiredMixin, MealMixin, ListBaseView):  # pylint: disable=too-many-ancestors
    """My meals view class."""

    context_object_name: str = "lmeals"
    model = user_meal.UserMeal
    template_name: str = "nutrition_tracker/my_meals.html"

    def get_queryset(self) -> QuerySet[user_meal.UserMeal]:
        luser: user_model.User = self.request.user  # type: ignore
        return user_meal.load_lmeals(luser, order_by="-meal_date")

    def get_results(self, context: dict[str, Any]) -> list:
        """Return meal browse results."""
        return [
            {
                "id": str(lmeal.external_id),
                "text": lmeal.display_name(with_date=True),
            }
            for lmeal in context[self.context_object_name]
        ]

    def paginate_queryset(self, queryset: QuerySet[user_meal.UserMeal], page_size: int) -> tuple[Paginator, int, list[user_meal.UserMeal], bool]:  # type: ignore
        (paginator, page, object_list, is_paginated) = super().paginate_queryset(queryset, page_size)
        object_list = model_utils.sort_meals(object_list, reverse=True)  # type: ignore
        return (paginator, page, object_list, is_paginated)  # type: ignore
