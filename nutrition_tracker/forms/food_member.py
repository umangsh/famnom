"""Food member form, process edits to memberships in recipes and meals."""
from __future__ import annotations

from typing import Any, Callable
from uuid import UUID

from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.utils.translation import gettext_lazy as _

from nutrition_tracker.logic import data_loaders, food_portion
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.models import (
    db_food,
    user_food_membership,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_recipe,
)
from nutrition_tracker.widgets import SelectWithOptionAttrs


class FoodMemberForm(forms.ModelForm):
    """Food member form."""

    child_external_id = forms.CharField(label=_("Name"), widget=forms.Select)
    quantity = forms.FloatField(label=_("Total Servings"), min_value=0, required=False)
    serving = forms.CharField(label=_("Serving Size"), widget=forms.Select)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        lparent: user_recipe.UserRecipe | user_meal.UserMeal | None = kwargs.pop("lparent", None)
        lfoods: list[user_ingredient.UserIngredient] = kwargs.pop("lfoods", [])
        lrecipes: list[user_recipe.UserRecipe] = kwargs.pop("lrecipes", [])
        super().__init__(*args, **kwargs)

        if self.instance.child_id:
            lobject_id: int = self.instance.child_id
            lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe | None = None
            cfood: db_food.DBFood | None = None

            if self.instance.child_type_id == data_loaders.get_content_type_ingredient_id():
                lobject = next((lfood for lfood in lfoods if lfood.id == lobject_id), None)
                cfood = lobject.db_food if lobject else None  # type: ignore
            elif self.instance.child_type_id == data_loaders.get_content_type_recipe_id():
                lobject = next((lrecipe for lrecipe in lrecipes if lrecipe.id == lobject_id), None)
                cfood = None

            if not lobject:
                return

            self.fields["child_external_id"].widget.choices = [(str(lobject.external_id), lobject.display_name)]
            self.fields["child_external_id"].initial = str(lobject.external_id)

            self.fields["serving"] = forms.ChoiceField(
                label=_("Serving Size"),
                widget=SelectWithOptionAttrs,
                choices=forms_logic.get_portion_choices_form_data(lobject, cfood=cfood),
            )

            if self.instance.portion:
                food_portions: list[
                    tuple[UUID, str, float | None, str | None, float | None, float | None]
                ] = food_portion.for_display_choices(lobject, cfood=cfood)
                if lparent:
                    member_portion: user_food_portion.UserFoodPortion | None = next(
                        (member.portions[0] for member in lparent.members if member.id == self.instance.id), None  # type: ignore
                    )
                    if member_portion:
                        portion: tuple = food_portion.get_food_member_portion(member_portion, food_portions)
                        if portion:
                            fp_tuple, quantity = portion
                            self.fields["serving"].initial = str(fp_tuple[0])
                            self.fields["quantity"].initial = quantity

    class Meta:
        model = user_food_membership.UserFoodMembership
        fields: list[str] = []


FoodMemberFormset: Callable = generic_inlineformset_factory(
    user_food_membership.UserFoodMembership,
    form=FoodMemberForm,
    ct_field="parent_type",
    fk_field="parent_id",
    extra=1,
    can_delete=True,
)


RecipeMemberFormset: Callable = generic_inlineformset_factory(
    user_food_membership.UserFoodMembership,
    form=FoodMemberForm,
    ct_field="parent_type",
    fk_field="parent_id",
    extra=1,
    can_delete=True,
)
