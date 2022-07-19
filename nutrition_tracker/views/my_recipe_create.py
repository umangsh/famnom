"""Create a new Recipe."""
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
    FoodPortionFormset,
    FoodPortionRecipeFormsetHelper,
    RecipeForm,
    RecipeMemberFormset,
)
from nutrition_tracker.views import CreateFormBaseView, NeverCacheMixin, RecipeMixin


class MyRecipeCreateView(NeverCacheMixin, LoginRequiredMixin, RecipeMixin, CreateFormBaseView):
    """View to create a new recipe."""

    form_class = RecipeForm
    template_name: str = "nutrition_tracker/my_recipe_create.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if self.request.POST:
            servings = FoodPortionFormset(self.request.POST, prefix="servings")
        else:
            servings = FoodPortionFormset(prefix="servings")

        if self.request.POST:
            food_members = FoodMemberFormset(self.request.POST, prefix="food")
        else:
            food_members = FoodMemberFormset(prefix="food")

        if self.request.POST:
            recipe_members = RecipeMemberFormset(self.request.POST, prefix="recipe")
        else:
            recipe_members = RecipeMemberFormset(prefix="recipe")

        context["servings"] = servings
        context["servings_helper"] = FoodPortionRecipeFormsetHelper(servings)
        context["food_members"] = food_members
        context["food_members_helper"] = CreateFoodMemberFormsetHelper(food_members)
        context["recipe_members"] = recipe_members
        context["recipe_members_helper"] = CreateRecipeMemberFormsetHelper(recipe_members)
        return context

    def form_valid(self, form: RecipeForm) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data()
        servings: BaseGenericInlineFormSet = context["servings"]
        food_members: BaseGenericInlineFormSet = context["food_members"]
        recipe_members: BaseGenericInlineFormSet = context["recipe_members"]

        if not food_members.is_valid() or not recipe_members.is_valid() or not servings.is_valid():
            return self.render_to_response(context)

        with transaction.atomic():
            self.lobject = form.save(servings, food_members, recipe_members)

        return super().form_valid(form)
