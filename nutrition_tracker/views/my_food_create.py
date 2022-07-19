"""UserIngredient create view."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.db import transaction
from django.http import HttpResponse

from nutrition_tracker.forms import FoodForm, FoodPortionFormset, FoodPortionFormsetHelper
from nutrition_tracker.views import CreateFormBaseView, IngredientMixin, NeverCacheMixin


class MyFoodCreateView(NeverCacheMixin, LoginRequiredMixin, IngredientMixin, CreateFormBaseView):
    """My ingredient create view class."""

    form_class = FoodForm
    template_name: str = "nutrition_tracker/my_food_create.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if self.request.POST:
            servings = FoodPortionFormset(self.request.POST)
        else:
            servings = FoodPortionFormset()

        context["servings"] = servings
        context["servings_helper"] = FoodPortionFormsetHelper(servings)
        return context

    def form_valid(self, form: FoodForm) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data()
        servings: BaseGenericInlineFormSet = context["servings"]
        if not servings.is_valid():
            return self.render_to_response(context)

        with transaction.atomic():
            self.lobject = form.save(servings)

        return super().form_valid(form)
