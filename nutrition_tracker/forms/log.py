"""Log form, process food/recipe logging into meals."""
from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from django import forms
from django.forms.widgets import Select
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import base
from nutrition_tracker.logic import food_portion
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.models import (
    db_food,
    user_food_membership,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)
from nutrition_tracker.widgets import SelectWithOptionAttrs


class LogForm(forms.Form):  # pylint: disable=too-many-instance-attributes
    """Log form."""

    external_id = forms.UUIDField(widget=forms.HiddenInput())
    meal_type = forms.CharField(label=_("Meal"), initial=constants.MealType.__empty__)
    meal_date = forms.DateField(
        label=_("Meal date"), initial=timezone.localdate(), input_formats=["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"]
    )
    quantity = forms.FloatField(label=_("Total Servings"), min_value=0, required=False)
    serving = forms.CharField(label=_("Serving Size"), initial=f"{constants.HUNDRED_SERVING_ID}")
    is_available = forms.BooleanField(
        label=_("More available for meal planning after this meal"), widget=forms.CheckboxInput(), required=False
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.external_id = kwargs.pop("external_id", None)
        self.lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe = kwargs.pop("lobject", None)
        self.cfood: db_food.DBFood = kwargs.pop("cfood", None)
        self.lmeal: user_meal.UserMeal = kwargs.pop("lmeal", None)
        self.lmembership: user_food_membership.UserFoodMembership = kwargs.pop("lmembership", None)
        self.food_portions: list[tuple[UUID, str, float | None, str | None, float | None, float | None]] = kwargs.pop(
            "food_portions", []
        )

        super().__init__(*args, **kwargs)
        self._init_details()
        self._init_food_portions()
        self.helper: base.LogFormHelper = base.LogFormHelper(self)

    def _init_details(self) -> None:
        """Initialize log form."""
        self.fields["external_id"].initial = self.external_id
        self.fields["meal_type"].widget = Select(choices=constants.MealType.choices)
        if self.lmeal:
            self.fields["meal_date"].initial = self.lmeal.meal_date
            self.fields["meal_type"].initial = self.lmeal.meal_type
        else:
            self.fields["meal_date"].initial = timezone.localdate()

        if self.lobject:
            luser_preference = user_preference.load_luser_preference(
                self.user, food_external_id=self.lobject.external_id
            )
            if luser_preference:
                self.fields["is_available"].initial = luser_preference.is_available()
        else:
            self.fields["is_available"].widget = forms.HiddenInput()

    def _init_food_portions(self) -> None:
        """Initialize food/recipe portions for logging meals."""
        self.fields["serving"].widget = SelectWithOptionAttrs(
            choices=forms_logic.get_portion_choices_form_data(self.lobject, cfood=self.cfood)
        )
        if self.lmembership:
            portion = food_portion.get_food_member_portion(self.lmembership.portions[0], self.food_portions)  # type: ignore
            if portion:
                serving, quantity = portion
                self.fields["serving"].initial = serving
                self.fields["quantity"].initial = quantity
        elif self.food_portions:
            self.fields["serving"].initial = self.food_portions[0][0]

    def save(self) -> None:
        """Save form: Log food/recipe in meal."""
        meal_type: constants.MealType = self.cleaned_data["meal_type"]
        meal_date: date = self.cleaned_data["meal_date"]
        quantity: float | None = self.cleaned_data["quantity"]
        serving: str = self.cleaned_data["serving"]

        if self.lobject and "is_available" in self.changed_data:
            is_available: bool | None = self.cleaned_data["is_available"]
            if is_available is not None:
                luser_preference, _unused = user_preference.get_or_create(
                    self.user, food_external_id=self.lobject.external_id
                )
                luser_preference.update_flag(user_preference.FLAG_IS_AVAILABLE, is_available)
                luser_preference.save()

        if not self.lobject and self.cfood:
            self.lobject = user_ingredient.create(luser=self.user, db_food=self.cfood)

        self.lmeal, _unused = user_meal.get_or_create(self.user, meal_date=meal_date, meal_type=meal_type)
        if not self.lmembership:
            self.lmembership = user_food_membership.create(self.user, parent=self.lmeal, child=self.lobject)

            lfood_portion: user_food_portion.UserFoodPortion = forms_logic.process_portion_choices_form_data(
                quantity, serving, self.lobject, cfood=self.cfood
            )

        elif self.lmembership.parent == self.lmeal:
            lfood_portion = forms_logic.process_portion_choices_form_data(
                quantity, serving, self.lobject, cfood=self.cfood, lfood_portion=self.lmembership.portions[0]  # type: ignore
            )

        else:
            old_meal_id: int = self.lmembership.parent_id
            self.lmembership.delete()

            # Delete meal also if this was the only membership.
            old_lmeal: user_meal.UserMeal | None = user_meal.load_lmeal(self.user, id_=old_meal_id)
            if not old_lmeal:
                return

            if len(old_lmeal.members) == 0:  # type: ignore
                old_lmeal.delete()

            self.lmembership = user_food_membership.create(self.user, parent=self.lmeal, child=self.lobject)

            lfood_portion = forms_logic.process_portion_choices_form_data(
                quantity, serving, self.lobject, cfood=self.cfood
            )

        lfood_portion.user = self.user
        lfood_portion.content_object = self.lmembership
        lfood_portion.save()
