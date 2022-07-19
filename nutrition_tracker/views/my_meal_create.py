"""Create a new Meal."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.db import transaction
from django.http import HttpResponse

from nutrition_tracker.forms import (
    CreateFoodMemberFormsetHelper,
    CreateRecipeMemberFormsetHelper,
    FoodMemberFormset,
    MealForm,
    RecipeMemberFormset,
)
from nutrition_tracker.views import CreateFormBaseView, MealMixin, NeverCacheMixin


class MyMealCreateView(NeverCacheMixin, LoginRequiredMixin, MealMixin, CreateFormBaseView):
    """View to create a new meal."""

    form_class = MealForm
    template_name: str = "nutrition_tracker/my_meal_create.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if self.request.POST:
            food_members = FoodMemberFormset(self.request.POST, prefix="food")
        else:
            food_members = FoodMemberFormset(prefix="food")

        if self.request.POST:
            recipe_members = RecipeMemberFormset(self.request.POST, prefix="recipe")
        else:
            recipe_members = RecipeMemberFormset(prefix="recipe")

        context["food_members"] = food_members
        context["food_members_helper"] = CreateFoodMemberFormsetHelper(food_members)
        context["recipe_members"] = recipe_members
        context["recipe_members_helper"] = CreateRecipeMemberFormsetHelper(recipe_members)
        return context

    def form_valid(self, form: MealForm) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data()
        food_members: BaseGenericInlineFormSet = context["food_members"]
        recipe_members: BaseGenericInlineFormSet = context["recipe_members"]

        if not food_members.is_valid() or not recipe_members.is_valid():
            return self.render_to_response(context)

        with transaction.atomic():
            self.lobject = form.save(food_members, recipe_members)

        return super().form_valid(form)
