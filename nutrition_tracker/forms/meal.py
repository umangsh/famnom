"""Meal form, process edits to user meals."""
from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import base, mixins
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_meal


class MealForm(forms.Form, mixins.MembersMixin):
    """Meal form."""

    external_id = forms.UUIDField(widget=forms.HiddenInput(), required=False)
    meal_type = forms.ChoiceField(label=_("Meal"), choices=constants.MealType.choices)
    meal_date = forms.DateField(label=_("Meal date"))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.lmeal: user_meal.UserMeal = kwargs.pop("lmeal", None)

        super().__init__(*args, **kwargs)
        self._init_details()
        self.helper: base.MealFormHelper = base.MealFormHelper(self)

    def _init_details(self) -> None:
        """Initialize meal metadata in form."""
        if self.lmeal:
            self.fields["external_id"].initial = self.lmeal.external_id
            self.fields["meal_date"].initial = self.lmeal.meal_date
            self.fields["meal_type"].initial = self.lmeal.meal_type
        else:
            self.fields["meal_date"].initial = timezone.localdate()

    def save(
        self, food_members: BaseGenericInlineFormSet, recipe_members: BaseGenericInlineFormSet
    ) -> user_meal.UserMeal:
        """Save form."""
        self._save_details()
        self._save_members(food_members, self.lmeal, data_loaders.get_content_type_ingredient())
        self._save_members(recipe_members, self.lmeal, data_loaders.get_content_type_recipe())
        return self.lmeal

    def _save_details(self) -> None:
        """Save meal metadata in form."""
        meal_type: constants.MealType = self.cleaned_data["meal_type"]
        meal_date: date = self.cleaned_data["meal_date"]
        if self.lmeal:
            if "meal_type" in self.changed_data or "meal_date" in self.changed_data:
                self.lmeal.meal_type = meal_type
                self.lmeal.meal_date = meal_date
                self.lmeal.save()
        else:
            self.lmeal, _unused = user_meal.get_or_create(self.user, meal_date=meal_date, meal_type=meal_type)
