"""UserRecipe edit view."""
from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.db import transaction
from django.http import HttpResponse

from nutrition_tracker.forms import (
    EditFoodMemberFormsetHelper,
    EditRecipeMemberFormsetHelper,
    FoodMemberFormset,
    FoodPortionFormset,
    FoodPortionRecipeFormsetHelper,
    RecipeForm,
    RecipeMemberFormset,
)
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership
from nutrition_tracker.views import EditFormBaseView, RecipeMixin


class MyRecipeEditView(RecipeMixin, EditFormBaseView):
    """My recipe edit view class."""

    form_class = RecipeForm
    template_name: str = "nutrition_tracker/my_recipe_edit.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if not self.request.user.is_authenticated:
            return context

        if self.request.POST:
            servings = FoodPortionFormset(self.request.POST, instance=self.lrecipe, prefix="servings")
        else:
            servings = FoodPortionFormset(instance=self.lrecipe, prefix="servings")

        if self.request.POST:
            food_members = FoodMemberFormset(
                self.request.POST,
                instance=self.lrecipe,
                prefix="food",
                form_kwargs={"lparent": self.lrecipe, "lfoods": self.lfoods},
            )
        else:
            food_members = FoodMemberFormset(
                instance=self.lrecipe,
                prefix="food",
                queryset=user_food_membership.load_lmemberships(
                    self.request.user,
                    parent_id=self.lrecipe.id,
                    parent_type_id=data_loaders.get_content_type_recipe_id(),
                    child_type_id=data_loaders.get_content_type_ingredient_id(),
                ),
                form_kwargs={"lparent": self.lrecipe, "lfoods": self.lfoods},
            )

        if self.request.POST:
            recipe_members = RecipeMemberFormset(
                self.request.POST,
                instance=self.lrecipe,
                prefix="recipe",
                form_kwargs={"lparent": self.lrecipe, "lrecipes": self.member_recipes},
            )
        else:
            recipe_members = RecipeMemberFormset(
                instance=self.lrecipe,
                prefix="recipe",
                queryset=user_food_membership.load_lmemberships(
                    self.request.user,
                    parent_id=self.lrecipe.id,
                    parent_type_id=data_loaders.get_content_type_recipe_id(),
                    child_type_id=data_loaders.get_content_type_recipe_id(),
                ),
                form_kwargs={"lparent": self.lrecipe, "lrecipes": self.member_recipes},
            )

        context["servings"] = servings
        context["servings_helper"] = FoodPortionRecipeFormsetHelper(servings)
        context["food_members"] = food_members
        context["food_members_helper"] = EditFoodMemberFormsetHelper(food_members)
        context["recipe_members"] = recipe_members
        context["recipe_members_helper"] = EditRecipeMemberFormsetHelper(recipe_members)
        return context

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "lrecipe": self.lrecipe,
            }
        )
        return kwargs

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
