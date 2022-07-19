"""Nutrition form module."""
from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.forms.widgets import Select
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import base, mixins
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.models import user_preference
from nutrition_tracker.utils import form as form_utils


class NutritionForm(mixins.ThresholdsMixin, forms.Form):
    """Nutrition edits form."""

    date_of_birth = forms.DateField(label=_("Date of Birth"))
    is_pregnant = forms.BooleanField(label=_("Pregnant"), widget=forms.CheckboxInput(), required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.nutrient_preferences: list[user_preference.UserPreference] = kwargs.pop("nutrient_preferences", [])

        super().__init__(*args, **kwargs)
        self._init_details()
        self._init_nutrients()
        self._init_thresholds(self.nutrient_preferences)
        self.helper: base.NutritionFormHelper = base.NutritionFormHelper(self)

    def _init_details(self) -> None:
        """Initialize nutrition metadata in form."""
        self.fields["date_of_birth"].initial = self.user.date_of_birth
        self.fields["is_pregnant"].initial = self.user.is_pregnant()

    def _init_nutrients(self) -> None:
        """Initialize nutrition preferences in form."""
        for nutrient_id in constants.TRACKER_NUTRIENT_IDS:
            if nutrient_id in constants.LOW_COVERAGE_NUTRIENT_IDS:
                continue

            nutrient_field_name: str = form_utils.get_field_name(nutrient_id)
            threshold_field_name: str = form_utils.get_threshold_field_name(nutrient_id)

            self.fields[threshold_field_name] = forms.CharField(label="", required=False)
            self.fields[threshold_field_name].widget = Select(choices=constants.Threshold.choices)
            self.fields[nutrient_field_name] = forms.FloatField(
                label=(f"{food_nutrient.for_display(nutrient_id)} ({food_nutrient.for_display_unit(nutrient_id)})"),
                min_value=0,
                required=False,
            )

    def save(self) -> None:
        """Save form."""
        self._save_details()
        self._save_nutrients()

    def _save_details(self) -> None:
        """Save nutrition metadata in form."""
        if "date_of_birth" not in self.changed_data and "is_pregnant" not in self.changed_data:
            return

        date_of_birth: date = self.cleaned_data["date_of_birth"]
        is_pregnant: bool = self.cleaned_data["is_pregnant"]
        if "date_of_birth" in self.changed_data:
            self.user.date_of_birth = date_of_birth

        if "is_pregnant" in self.changed_data:
            self.user.update_flag(user_model.User.FLAG_IS_PREGNANT, is_pregnant)

        self.user.save()

    def _save_nutrients(self) -> None:
        """Save nutrition preferences in form."""
        if not self.changed_data:
            return

        ids: list[int] = list(set(constants.TRACKER_NUTRIENT_IDS) - set(constants.LOW_COVERAGE_NUTRIENT_IDS))
        self._save_thresholds(self.user, ids, constants.THRESHOLD_ID_NUTRIENT)
