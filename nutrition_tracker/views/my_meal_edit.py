"""UserMeal edit view."""
from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.db import transaction
from django.http import HttpResponse

from nutrition_tracker.forms import (
    EditFoodMemberFormsetHelper,
    EditRecipeMemberFormsetHelper,
    FoodMemberFormset,
    MealForm,
    RecipeMemberFormset,
)
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership
from nutrition_tracker.views import EditFormBaseView, MealMixin


class MyMealEditView(MealMixin, EditFormBaseView):
    """My meal edit view class."""

    form_class = MealForm
    template_name: str = "nutrition_tracker/my_meal_edit.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if not self.request.user.is_authenticated:
            return context

        if self.request.POST:
            food_members = FoodMemberFormset(
                self.request.POST,
                instance=self.lmeal,
                prefix="food",
                form_kwargs={"lparent": self.lmeal, "lfoods": self.lfoods},
            )
        else:
            food_members = FoodMemberFormset(
                instance=self.lmeal,
                prefix="food",
                queryset=user_food_membership.load_lmemberships(
                    self.request.user,
                    parent_id=self.lmeal.id,
                    parent_type_id=data_loaders.get_content_type_meal_id(),
                    child_type_id=data_loaders.get_content_type_ingredient_id(),
                ),
                form_kwargs={"lparent": self.lmeal, "lfoods": self.lfoods},
            )

        if self.request.POST:
            recipe_members = RecipeMemberFormset(
                self.request.POST,
                instance=self.lmeal,
                prefix="recipe",
                form_kwargs={"lparent": self.lmeal, "lrecipes": self.member_recipes},
            )
        else:
            recipe_members = RecipeMemberFormset(
                instance=self.lmeal,
                prefix="recipe",
                queryset=user_food_membership.load_lmemberships(
                    self.request.user,
                    parent_id=self.lmeal.id,
                    parent_type_id=data_loaders.get_content_type_meal_id(),
                    child_type_id=data_loaders.get_content_type_recipe_id(),
                ),
                form_kwargs={"lparent": self.lmeal, "lrecipes": self.member_recipes},
            )

        context["food_members"] = food_members
        context["food_members_helper"] = EditFoodMemberFormsetHelper(food_members)
        context["recipe_members"] = recipe_members
        context["recipe_members_helper"] = EditRecipeMemberFormsetHelper(recipe_members)
        return context

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "lmeal": self.lmeal,
            }
        )
        return kwargs

    def form_valid(self, form: MealForm) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data()
        food_members: BaseGenericInlineFormSet = context["food_members"]
        recipe_members: BaseGenericInlineFormSet = context["recipe_members"]

        if not food_members.is_valid() or not recipe_members.is_valid():
            return self.render_to_response(context)

        with transaction.atomic():
            self.lobject = form.save(food_members, recipe_members)

        return super().form_valid(form)
