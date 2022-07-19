"""Mealplan forms, to calculate mealplans."""
from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import base, mixins
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import (
    user_food_membership,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)
from nutrition_tracker.utils import form as form_utils
from nutrition_tracker.utils import text


class MealplanForm(forms.Form):
    """Mealplan base form."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.lmealplan = kwargs.pop("lmealplan", None)
        super().__init__(*args, **kwargs)


class MealplanFormOne(MealplanForm):
    """Mealplan one form - available, etc foods/recipes"""

    available_foods = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )
    available_recipes = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )

    must_have_foods = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )
    must_have_recipes = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )

    dont_have_foods = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )
    dont_have_recipes = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )

    dont_repeat_foods = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )
    dont_repeat_recipes = SimpleArrayField(
        forms.UUIDField(),
        label=_(""),
        widget=forms.SelectMultiple,
        required=False,
        max_length=constants.FORM_MAX_UUIDS,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper: base.MealplanFormOneHelper = base.MealplanFormOneHelper(self)

    def save(self) -> None:
        """Save form."""
        self._save_preferences()

    def _save_preferences(self) -> None:  # pylint: disable=too-many-locals
        """Save food/recipe preferences.
        Available/Must have/Dont have/Dont repeat food/recipe preferences."""
        food_preferences: list[user_preference.UserPreference] = list(user_prefs.load_food_preferences(self.user))
        (
            available_items,
            must_have_items,
            dont_have_items,
            dont_repeat_items,
        ) = forms_logic.get_items_form_data_from_preferences(food_preferences)

        available_foods: list[UUID] = self.cleaned_data["available_foods"]
        available_recipes: list[UUID] = self.cleaned_data["available_recipes"]
        must_have_foods: list[UUID] = self.cleaned_data["must_have_foods"]
        must_have_recipes: list[UUID] = self.cleaned_data["must_have_recipes"]
        dont_have_foods: list[UUID] = self.cleaned_data["dont_have_foods"]
        dont_have_recipes: list[UUID] = self.cleaned_data["dont_have_recipes"]
        dont_repeat_foods: list[UUID] = self.cleaned_data["dont_repeat_foods"]
        dont_repeat_recipes: list[UUID] = self.cleaned_data["dont_repeat_recipes"]

        updated_available_items: set[UUID] = set(available_foods).union(available_recipes)
        updated_must_have_items: set[UUID] = set(must_have_foods).union(must_have_recipes)
        updated_dont_have_items: set[UUID] = set(dont_have_foods).union(dont_have_recipes)
        updated_dont_repeat_items: set[UUID] = set(dont_repeat_foods).union(dont_repeat_recipes)

        items: set[UUID] = (
            (updated_available_items - set(available_items))
            .union(updated_must_have_items - set(must_have_items))
            .union(updated_dont_have_items - set(dont_have_items))
            .union(updated_dont_repeat_items - set(dont_repeat_items))
        )
        created: list[user_preference.UserPreference] = []
        for item in items:
            fp_obj: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
                food_preferences, food_external_id=item
            )
            if fp_obj:
                continue

            up_obj: user_preference.UserPreference = user_preference.UserPreference(
                user=self.user, food_external_id=item
            )
            if item in updated_available_items:
                up_obj.add_flag(user_preference.FLAG_IS_AVAILABLE)

            if item in updated_must_have_items:
                up_obj.add_flag(user_preference.FLAG_IS_NOT_ZEROABLE)

            if item in updated_dont_have_items:
                up_obj.add_flag(user_preference.FLAG_IS_NOT_ALLOWED)

            if item in updated_dont_repeat_items:
                up_obj.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)

            created.append(up_obj)

        user_preference.bulk_create(created)

        updated: set[user_preference.UserPreference] = set()
        updated_ids: set[UUID] = set()
        self._fill_db_updates(
            updated_available_items,
            set(available_items),
            user_preference.FLAG_IS_AVAILABLE,
            food_preferences,
            updated,
            updated_ids,
        )
        self._fill_db_updates(
            updated_must_have_items,
            set(must_have_items),
            user_preference.FLAG_IS_NOT_ZEROABLE,
            food_preferences,
            updated,
            updated_ids,
        )
        self._fill_db_updates(
            updated_dont_have_items,
            set(dont_have_items),
            user_preference.FLAG_IS_NOT_ALLOWED,
            food_preferences,
            updated,
            updated_ids,
        )
        self._fill_db_updates(
            updated_dont_repeat_items,
            set(dont_repeat_items),
            user_preference.FLAG_IS_NOT_REPEATABLE,
            food_preferences,
            updated,
            updated_ids,
        )

        user_preference.bulk_update(list(updated), ["flags"])

    def _fill_db_updates(  # pylint: disable=too-many-arguments,no-self-use
        self,
        form_items: set[UUID],
        db_items: set[UUID],
        flag_name: str,
        food_preferences: list[user_preference.UserPreference],
        updated: set[user_preference.UserPreference],
        updated_ids: set[UUID],
    ) -> None:
        """Calculates updates to preferences to be applied to the database, based on changes (form_items) and existing data (db_items)."""
        items: set[UUID] = form_items - db_items
        for item in items:
            fp_obj: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
                food_preferences, food_external_id=item
            )
            if fp_obj:
                fp_obj.add_flag(flag_name)
                if fp_obj.food_external_id and fp_obj.food_external_id not in updated_ids:
                    updated_ids.add(fp_obj.food_external_id)
                    updated.add(fp_obj)

        items = db_items - form_items
        for item in items:
            fp_obj = user_prefs.filter_preferences_by_id(food_preferences, food_external_id=item)
            if fp_obj:
                fp_obj.remove_flag(flag_name)
                if fp_obj.food_external_id and fp_obj.food_external_id not in updated_ids:
                    updated_ids.add(fp_obj.food_external_id)
                    updated.add(fp_obj)


class MealplanFormTwo(mixins.ThresholdsMixin, MealplanForm):
    """Mealplan two form - taste preferences, quantity thresholds."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        food_preferences: list[user_preference.UserPreference] = list(user_prefs.load_food_preferences(self.user))
        usable_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
            food_preferences, flags_set_any=[user_preference.FLAG_IS_AVAILABLE, user_preference.FLAG_IS_NOT_ZEROABLE]
        )
        self._init_preferences(usable_preferences)
        self._init_thresholds(usable_preferences)

    def _init_preferences(self, food_preferences: list[user_preference.UserPreference]) -> None:
        items: list[UUID] = [fp.food_external_id for fp in food_preferences if fp.food_external_id]

        rows: list[UUID] = []
        lfoods: list[user_ingredient.UserIngredient] = list(user_ingredient.load_lfoods(self.user, external_ids=items))
        for lfood in lfoods:
            rows.append(lfood.external_id)
            field_name: str = form_utils.get_field_name(lfood.external_id)
            threshold_field_name: str = form_utils.get_threshold_field_name(lfood.external_id)
            self.fields[field_name] = forms.FloatField(label=lfood.display_name, min_value=0, required=False)
            self.fields[threshold_field_name] = forms.ChoiceField(
                label="", choices=constants.Threshold.choices, required=False
            )

        lrecipes: list[user_recipe.UserRecipe] = list(user_recipe.load_lrecipes(self.user, external_ids=items))
        for lrecipe in lrecipes:
            rows.append(lrecipe.external_id)
            field_name = form_utils.get_field_name(lrecipe.external_id)
            threshold_field_name = form_utils.get_threshold_field_name(lrecipe.external_id)
            self.fields[field_name] = forms.FloatField(label=lrecipe.display_name, min_value=0, required=False)
            self.fields[threshold_field_name] = forms.ChoiceField(
                label="", choices=constants.Threshold.choices, required=False
            )

        self.helper: base.MealplanFormTwoHelper = base.MealplanFormTwoHelper(rows, self)

    def save(self) -> None:
        """Save form."""
        self._save_preferences()

    def _save_preferences(self) -> None:
        """Save food/recipe amount threshold preferences."""
        if not self.changed_data:
            return

        ids: set[str] = set({f.replace("threshold_", "") for f in self.changed_data})
        external_ids: list[UUID] = [UUID(f, version=4) for f in ids if text.is_valid_uuid(f)]
        self._save_thresholds(self.user, external_ids, constants.THRESHOLD_ID_FOOD)


class MealplanFormThree(MealplanForm):
    """Mealplan three form - save mealplan to meals."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._init_mealplan()

    # flake8: noqa: C901
    def _init_mealplan(self) -> None:  # pylint: disable=too-many-branches
        """Initialize form with computed mealplan."""
        rows: list[UUID] = []
        if self.lmealplan:
            for lfood in self.lmealplan.lfoods:
                if lfood.external_id not in self.lmealplan.quantity_map:
                    continue

                quantity: float = self.lmealplan.quantity_map.get(lfood.external_id, 0)
                for lmeal in self.lmealplan.lmeals_today:
                    for lmeal_member in lmeal.members:
                        if lmeal_member.child_id == lfood.id and (
                            lmeal_member.child_type_id == data_loaders.get_content_type_ingredient_id()
                        ):
                            quantity -= lmeal_member.portions[0].serving_size

                r_quantity: int = round(quantity)
                if r_quantity == 0:
                    continue

                rows.append(lfood.external_id)
                field_name: str = form_utils.get_field_name(lfood.external_id)
                self.fields[field_name] = forms.FloatField(
                    label=lfood.display_name, min_value=0, initial=r_quantity, required=False
                )
                meal_field_name: str = form_utils.get_meal_field_name(lfood.external_id)
                self.fields[meal_field_name] = forms.ChoiceField(
                    label="", choices=constants.MealType.choices, required=False
                )

            for lrecipe in self.lmealplan.lrecipes:
                if lrecipe.external_id not in self.lmealplan.quantity_map:
                    continue

                quantity = self.lmealplan.quantity_map.get(lrecipe.external_id, 0)
                for lmeal in self.lmealplan.lmeals_today:
                    for lmeal_member in lmeal.members:
                        if lmeal_member.child_id == lrecipe.id and (
                            lmeal_member.child_type_id == data_loaders.get_content_type_recipe_id()
                        ):
                            quantity -= lmeal_member.portions[0].serving_size

                r_quantity = round(quantity)
                if r_quantity == 0:
                    continue

                rows.append(lrecipe.external_id)
                field_name = form_utils.get_field_name(lrecipe.external_id)
                self.fields[field_name] = forms.FloatField(
                    label=lrecipe.display_name(),
                    min_value=0,
                    initial=r_quantity,
                    required=False,
                )
                meal_field_name = form_utils.get_meal_field_name(lrecipe.external_id)
                self.fields[meal_field_name] = forms.ChoiceField(
                    label="", choices=constants.MealType.choices, required=False
                )

        self.helper: base.MealplanFormThreeHelper = base.MealplanFormThreeHelper(rows, self)

    def save(self) -> bool:
        """Save form."""
        return self._save_mealplan()

    def _save_mealplan(self) -> bool:  # pylint: disable=too-many-locals,too-many-branches
        """Save mealplan to selected meals.

        The rendered mealplan is gone once the form is rendered, so cleaned_data and changed_data aren't populated. Iterate through form.data and validate fields manually."""
        changed: bool = False
        if not self.data:
            return changed

        external_ids: list[str] = [f for f in self.data if text.is_valid_uuid(f)]
        if not external_ids:
            return changed

        lobject_ids: list[UUID] = []
        for external_id in external_ids:
            quantity: float | None = text.valid_float(self.data[external_id])
            if not quantity:
                continue

            lobject_ids.append(UUID(external_id, version=4))

        lobjects: dict[UUID, user_ingredient.UserIngredient | user_recipe.UserRecipe] = {}
        lfoods: list[user_ingredient.UserIngredient] = list(
            user_ingredient.load_lfoods(self.user, external_ids=lobject_ids)
        )
        lrecipes: list[user_recipe.UserRecipe] = list(user_recipe.load_lrecipes(self.user, external_ids=lobject_ids))
        for lfood in lfoods:
            lobjects[lfood.external_id] = lfood

        for lrecipe in lrecipes:
            lobjects[lrecipe.external_id] = lrecipe

        lmeals: dict[constants.MealType, user_meal.UserMeal] = {}
        meal_date: date = timezone.localdate()
        for external_id_uuid in lobject_ids:
            external_id = str(external_id_uuid)
            quantity = text.valid_float(self.data[external_id])
            field_name: str = form_utils.get_meal_field_name(external_id)
            raw_meal_type: constants.MealType = self.data[field_name]
            if not raw_meal_type:
                continue

            if raw_meal_type == constants.MealType.__empty__:
                continue

            for type_, _unused in constants.MealType.choices:
                if not type_:
                    continue

                meal_type_: constants.MealType = constants.MealType(type_)
                if not raw_meal_type == meal_type_:
                    continue

                if meal_type_ in lmeals:
                    lmeal = lmeals[meal_type_]
                else:
                    lmeal, _unused_created = user_meal.get_or_create(
                        self.user, meal_date=meal_date, meal_type=meal_type_
                    )
                    lmeals[meal_type_] = lmeal

                changed = True
                lmembership: user_food_membership.UserFoodMembership = user_food_membership.create(
                    self.user, parent=lmeal, child=lobjects[external_id_uuid]
                )
                lfood_portion: user_food_portion.UserFoodPortion = forms_logic.process_portion_choices_form_data(
                    quantity, str(constants.ONE_SERVING_ID), lobjects[external_id_uuid]
                )
                lfood_portion.user = self.user
                lfood_portion.content_object = lmembership
                lfood_portion.save()

        return changed
