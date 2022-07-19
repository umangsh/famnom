"""Form layout mixins for crispy forms."""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Sequence
from uuid import UUID

from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import (
    db_food_portion,
    user_food_membership,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_preference,
    user_preference_threshold,
    user_recipe,
)
from nutrition_tracker.utils import form as form_utils


class ServingsMixin:  # pylint: disable=too-few-public-methods
    """Servings formset mixin for foods/recipes."""

    def _save_servings(  # pylint: disable=no-self-use
        self,
        servings: BaseGenericInlineFormSet,
        instance: user_ingredient.UserIngredient | user_recipe.UserRecipe,
        content_type: ContentType,
        is_new_lfood: bool = False,
    ) -> Any:
        """Save formset."""
        if is_new_lfood:
            for serving_form in servings.forms:
                if not serving_form.has_changed():
                    continue

                if serving_form.cleaned_data.get("DELETE"):
                    continue

                servings_per_container: float | None = serving_form.cleaned_data["servings_per_container"]
                serving_size: float = serving_form.cleaned_data["serving_size"]
                serving_size_unit: str = serving_form.cleaned_data["serving_size_unit"]
                measure_unit_id: str | None = serving_form.cleaned_data["measure_unit"]
                household_quantity: str | None = serving_form.cleaned_data["household_quantity"]

                measure_unit_id = measure_unit_id if measure_unit_id else None
                amount: float | None = float(Fraction(household_quantity)) if household_quantity else None

                db_food_portion.create(
                    db_food=instance.db_food,  # type: ignore
                    source_type=constants.DBFoodSourceType.USER,
                    servings_per_container=servings_per_container,
                    serving_size=serving_size,
                    serving_size_unit=serving_size_unit,
                    measure_unit_id=measure_unit_id,
                    amount=amount,
                )

            return servings

        servings.instance = instance
        for serving_form in servings.forms:
            if not serving_form.has_changed():
                continue

            if serving_form.cleaned_data.get("DELETE"):
                continue

            serving_form.instance.user = instance.user
            serving_form.instance.content_type = content_type
            serving_form.instance.object_id = instance.id
            serving_form.save(commit=False)

        return servings.save()


class MembersMixin:  # pylint: disable=too-few-public-methods
    """Members formset mixin for recipes/meals."""

    def _save_members(  # pylint: disable=no-self-use
        self,
        members: BaseGenericInlineFormSet,
        instance: user_recipe.UserRecipe | user_meal.UserMeal,
        content_type: ContentType,
    ) -> BaseGenericInlineFormSet:
        """Save formset."""
        members.instance = instance
        for member_form in members.forms:
            if not member_form.has_changed():
                continue

            if member_form.cleaned_data.get("DELETE"):
                continue

            if not instance.user:
                continue

            child_external_id: str = member_form.cleaned_data["child_external_id"]
            # Bail early for self-referential additions.
            # Can only really happen when editing recipes, to include the
            # same recipe as a member.
            if str(child_external_id) == str(instance.external_id):
                return members

            quantity: float | None = member_form.cleaned_data["quantity"]
            serving: str = member_form.cleaned_data["serving"]

            lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe | None = None
            if content_type == data_loaders.get_content_type_ingredient():
                lobject = user_ingredient.load_lfood(instance.user, external_id=child_external_id)
            elif content_type == data_loaders.get_content_type_recipe():
                lobject = user_recipe.load_lrecipe(instance.user, external_id=child_external_id)

            if not lobject:
                continue

            if "child_external_id" in member_form.changed_data:
                member_form.instance.user = instance.user
                member_form.instance.parent = instance
                member_form.instance.child = lobject

            lmembership: user_food_membership.UserFoodMembership = member_form.save()

            if "quantity" in member_form.changed_data or "serving" in member_form.changed_data:
                lfood_portion: user_food_portion.UserFoodPortion = forms_logic.process_portion_choices_form_data(
                    quantity, str(serving), lobject, cfood=getattr(lobject, "db_food", None)
                )
                user_food_portion.update_or_create(
                    instance.user,
                    content_type=data_loaders.get_content_type_membership(),
                    object_id=lmembership.id,
                    defaults={
                        "serving_size": lfood_portion.serving_size,
                        "serving_size_unit": lfood_portion.serving_size_unit,
                        "quantity": lfood_portion.quantity,
                        "amount": lfood_portion.amount,
                        "measure_unit_id": lfood_portion.measure_unit_id,
                        "portion_description": lfood_portion.portion_description,
                        "modifier": lfood_portion.modifier,
                    },
                )

        return members.save()


# Disable mypy type check.
# ThresholdsMixin reads self.fields, self.changed_data and self.cleaned_data from
# associated form (Mealplan form, forms.form) in mealplan and nutrition
# forms. This implicit dependency should be broken and fixed.
class ThresholdsMixin:  # pylint: disable=too-few-public-methods
    """Thresholds form mixin for nutrition/mealplan."""

    def _init_thresholds(self, preferences: list[user_preference.UserPreference]) -> None:
        """Initialize thresholds form."""
        if not preferences:
            return

        for lfood_preference in preferences:
            field_id: UUID | int | None = (
                getattr(lfood_preference, "food_external_id", None)
                or getattr(lfood_preference, "food_category_id", None)
                or getattr(lfood_preference, "food_nutrient_id", None)
            )
            if not field_id:
                continue

            field_name: str = form_utils.get_field_name(field_id)
            threshold_field_name: str = form_utils.get_threshold_field_name(field_id)
            threshold: None | (
                user_preference_threshold.UserPreferenceThreshold
            ) = user_prefs.filter_preference_thresholds(list(lfood_preference.userpreferencethreshold_set.all()))

            if not threshold:
                continue

            if threshold.exact_value:
                self.fields[field_name].initial = threshold.exact_value  # type: ignore
                self.fields[threshold_field_name].initial = constants.Threshold.EXACT_VALUE  # type: ignore

            elif threshold.min_value:
                self.fields[field_name].initial = threshold.min_value  # type: ignore
                self.fields[threshold_field_name].initial = constants.Threshold.MIN_VALUE  # type: ignore

            elif threshold.max_value:
                self.fields[field_name].initial = threshold.max_value  # type: ignore
                self.fields[threshold_field_name].initial = constants.Threshold.MAX_VALUE  # type: ignore

    def _save_thresholds(self, luser: user_model.User, ids: Sequence[int | str | UUID], id_type: int) -> None:
        """Save updated thresholds."""
        ids = ids or []
        if not ids:
            return

        if id_type not in (
            constants.THRESHOLD_ID_FOOD,
            constants.THRESHOLD_ID_CATEGORY,
            constants.THRESHOLD_ID_NUTRIENT,
        ):
            return

        for field_id in ids:
            field_name: str = form_utils.get_field_name(field_id)
            threshold_field_name: str = form_utils.get_threshold_field_name(field_id)
            if field_name not in self.changed_data and threshold_field_name not in self.changed_data:  # type: ignore
                continue

            threshold_value: float | None = self.cleaned_data[field_name]  # type: ignore
            threshold_field: str | None = self.cleaned_data[threshold_field_name]  # type: ignore
            threshold_field = threshold_field if threshold_field else None
            if id_type == constants.THRESHOLD_ID_FOOD:
                luser_preference, _unused = user_preference.get_or_create(luser, food_external_id=field_id)
            elif id_type == constants.THRESHOLD_ID_CATEGORY:
                luser_preference, _unused = user_preference.get_or_create(luser, food_category_id=field_id)
            elif id_type == constants.THRESHOLD_ID_NUTRIENT:
                luser_preference, _unused = user_preference.get_or_create(luser, food_nutrient_id=field_id)

            luser_preference_threshold, _unused = user_preference_threshold.get_or_create(
                luser,
                user_preference=luser_preference,
                num_days=1,
                dimension=constants.Dimension.QUANTITY,
                expansion_set=constants.ExpansionSet.SELF,
            )

            if threshold_field is None and threshold_value is None:
                luser_preference_threshold.delete()
            else:
                if threshold_field == constants.Threshold.EXACT_VALUE:
                    luser_preference_threshold.exact_value = threshold_value
                    luser_preference_threshold.min_value = None
                    luser_preference_threshold.max_value = None
                elif threshold_field == constants.Threshold.MIN_VALUE:
                    luser_preference_threshold.exact_value = None
                    luser_preference_threshold.min_value = threshold_value
                    luser_preference_threshold.max_value = None
                elif threshold_field == constants.Threshold.MAX_VALUE:
                    luser_preference_threshold.exact_value = None
                    luser_preference_threshold.min_value = None
                    luser_preference_threshold.max_value = threshold_value

                luser_preference_threshold.save()
