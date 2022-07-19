"""Common logic module for mealplanning."""
from __future__ import annotations

from uuid import UUID

from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, user_prefs
from nutrition_tracker.models import (
    user_ingredient,
    user_meal,
    user_preference,
    user_preference_threshold,
    user_recipe,
)
from nutrition_tracker.utils import nutrition as nutrition_utils
from nutrition_tracker.utils import planner as planner_utils


def restrict_to_repeatable_or_unused(
    external_ids: list[UUID],
    food_preferences: list[user_preference.UserPreference],
    lfoods: list[user_ingredient.UserIngredient],
    lrecipes: list[user_recipe.UserRecipe],
) -> set[UUID]:
    """Restrict external_ids to repeatable or unused foods i.e. remove foods that were consumed the previous day and are not repeatable."""
    r_food_ids: set[UUID] = set()
    for external_id in external_ids:
        food_preference: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
            food_preferences, food_external_id=external_id
        )

        if food_preference:
            is_repeatable: bool = not food_preference.is_not_repeatable()
            is_non_repeatable_and_unused_previous_day: bool = food_preference.is_not_repeatable() and (
                all(f.external_id != external_id for f in lfoods)
                and all(f.external_id != external_id for f in lrecipes)
            )
        else:
            is_repeatable = True

        if is_repeatable or is_non_repeatable_and_unused_previous_day:
            r_food_ids.add(external_id)

    return r_food_ids


def add_from_history(
    external_ids: list[UUID],
    today_meals: list[user_meal.UserMeal],
    lfoods: list[user_ingredient.UserIngredient],
    lrecipes: list[user_recipe.UserRecipe],
) -> set[UUID]:
    """Add previously consumed foods / recipes in the day from history."""
    r_food_ids: set[UUID] = set(external_ids)
    for lmeal in today_meals:
        for lmember in lmeal.members:  # type: ignore
            for lfood in lfoods:
                if (
                    lfood.id == lmember.child_id
                    and lmember.child_type_id == data_loaders.get_content_type_ingredient_id()
                ):
                    r_food_ids.add(lfood.external_id)
                    break

            for lrecipe in lrecipes:
                if (
                    lrecipe.id == lmember.child_id
                    and lmember.child_type_id == data_loaders.get_content_type_recipe_id()
                ):
                    r_food_ids.add(lrecipe.external_id)
                    break

    return r_food_ids


def setup_threshold_constraint_base(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    variable_name: str,
    base_id: int | str | UUID,
    threshold: user_preference_threshold.UserPreferenceThreshold,
    history: int = 0,
    multiplier: int = 1,
    enforce_exact: bool = False,
) -> None:
    """Setup threshold constraint base."""
    if threshold.exact_value is not None:
        exact_value: float = max(threshold.exact_value, history)
        exact_value = nutrition_utils.process_exact_threshold_value(exact_value) * multiplier
        constraint_variable: str = planner_utils.get_constraint_variable(base_id)
        variables[constraint_variable] = model.NewBoolVar(constraint_variable)
        model.Add(variables[variable_name] == exact_value).OnlyEnforceIf(variables[constraint_variable])
        model.Add(variables[variable_name] != exact_value).OnlyEnforceIf(variables[constraint_variable].Not())

    if threshold.min_value is not None:
        min_value: float = max(threshold.min_value, history)
        min_value = nutrition_utils.process_min_threshold_value(min_value) * multiplier
        constraint_variable = planner_utils.get_constraint_variable(base_id)
        variables[constraint_variable] = model.NewBoolVar(constraint_variable)
        model.Add(variables[variable_name] >= min_value).OnlyEnforceIf(variables[constraint_variable])
        model.Add(variables[variable_name] < min_value).OnlyEnforceIf(variables[constraint_variable].Not())

    if threshold.max_value is not None:
        max_value: float = max(threshold.max_value, history)
        max_value = nutrition_utils.process_max_threshold_value(max_value) * multiplier
        constraint_variable = planner_utils.get_constraint_variable(base_id)
        variables[constraint_variable] = model.NewBoolVar(constraint_variable)
        model.Add(variables[variable_name] <= max_value).OnlyEnforceIf(variables[constraint_variable])
        model.Add(variables[variable_name] > max_value).OnlyEnforceIf(variables[constraint_variable].Not())

    if enforce_exact:
        model.Add(variables[constraint_variable] == 1)


def setup_default_food_constraints(
    model: cp_model.CpModel, variables: dict, variable_name: str, history: int = 0
) -> None:
    """Setup default food constraints."""
    model.Add(variables[variable_name] >= max(history, constants.DEFAULT_DAILY_FOOD_MIN_VALUE))
    model.Add(variables[variable_name] <= max(history, constants.DEFAULT_DAILY_FOOD_MAX_VALUE))


def get_threshold_intervals(
    luser_preference: user_preference.UserPreference,
    threshold: user_preference_threshold.UserPreferenceThreshold | None,
) -> list[list]:
    """Get threshold intervals."""
    intervals: list[list] = []
    if not threshold:
        if luser_preference.food_external_id:
            return [[constants.DEFAULT_DAILY_FOOD_MIN_VALUE, constants.DEFAULT_DAILY_FOOD_MAX_VALUE]]

        return [[constants.INT_MIN_VALUE, constants.INT_MAX_VALUE]]

    if threshold.exact_value is not None:
        exact_value: int = nutrition_utils.process_exact_threshold_value(threshold.exact_value)
        intervals.extend([[exact_value]])
    else:
        min_default = constants.INT_MIN_VALUE
        if (
            luser_preference.food_external_id
            and threshold.max_value
            and threshold.max_value > constants.DEFAULT_DAILY_FOOD_MIN_VALUE
        ):
            min_default = constants.DEFAULT_DAILY_FOOD_MIN_VALUE
        min_value: int = nutrition_utils.process_min_threshold_value(threshold.min_value, default=min_default)

        max_default = constants.INT_MAX_VALUE
        if luser_preference.food_external_id:
            max_default = constants.DEFAULT_DAILY_FOOD_MAX_VALUE
        max_value: int = nutrition_utils.process_max_threshold_value(threshold.max_value, default=max_default)

        intervals.extend([[min_value, max_value]])

    return intervals
