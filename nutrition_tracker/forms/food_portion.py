"""Food portion form, process edits to portions/servings in foods, meals and recipes."""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.utils.translation import gettext_lazy as _

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion
from nutrition_tracker.models import user_food_portion


class FoodPortionForm(forms.ModelForm):
    """Food portion form."""

    servings_per_container = forms.FloatField(label=_("Servings per container"), min_value=0, required=False)
    serving_size = forms.FloatField(label=_("Serving size"), min_value=0)
    serving_size_unit = forms.ChoiceField(label=_("Serving unit"), choices=constants.ServingSizeUnit.choices)
    household_quantity = forms.ChoiceField(label=_("Household quantity"), required=False)
    measure_unit = forms.ChoiceField(label=_("Household unit"), required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["servings_per_container"].initial = self.instance.servings_per_container
        self.fields["serving_size"].initial = self.instance.serving_size
        self.fields["serving_size_unit"].initial = self.instance.serving_size_unit

        choices: list[tuple[str, str]] = [("", _("Select quantity"))]
        choices.extend([(unit_name, unit_name) for unit_name in constants.FORM_SERVING_SIZE_UNITS])
        self.fields["household_quantity"].choices = choices
        self.fields["household_quantity"].initial = next(
            (
                unit_name
                for unit_name in constants.FORM_SERVING_SIZE_UNITS
                if self.instance.amount == float(Fraction(unit_name))
            ),
            "",
        )

        choices = [("", _("Select unit"))]
        choices.extend([(str(m.id_), m.name) for m in food_portion.get_measure_units_sorted_by_name()])
        self.fields["measure_unit"].choices = choices
        self.fields["measure_unit"].initial = str(self.instance.measure_unit_id or "")

    def save(self, commit: bool = True) -> user_food_portion.UserFoodPortion:
        model_: user_food_portion.UserFoodPortion = super().save(commit=False)

        servings_per_container: float | None = self.cleaned_data["servings_per_container"]
        serving_size: float = self.cleaned_data["serving_size"]
        serving_size_unit: str = self.cleaned_data["serving_size_unit"]
        _measure_unit_id: str | None = self.cleaned_data["measure_unit"]
        household_quantity: str | None = self.cleaned_data["household_quantity"]

        measure_unit_id: str | None = _measure_unit_id if _measure_unit_id else None
        amount: float | None = float(Fraction(household_quantity)) if household_quantity else None

        self.instance.servings_per_container = servings_per_container
        self.instance.serving_size = serving_size
        self.instance.serving_size_unit = serving_size_unit
        self.instance.measure_unit_id = measure_unit_id if measure_unit_id else None
        self.instance.amount = amount

        if commit:
            model_.save()
        return model_

    class Meta:
        model = user_food_portion.UserFoodPortion
        fields: list[str] = [
            "servings_per_container",
            "serving_size",
            "serving_size_unit",
            "household_quantity",
            "measure_unit",
        ]


FoodPortionFormset: Callable = generic_inlineformset_factory(
    user_food_portion.UserFoodPortion, form=FoodPortionForm, extra=1, can_delete=True
)
