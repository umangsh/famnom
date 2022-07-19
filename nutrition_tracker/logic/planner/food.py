"""Food logic module for mealplanning."""
from __future__ import annotations

from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_portion, user_prefs
from nutrition_tracker.logic.planner import common as common_planner
from nutrition_tracker.models import (
    user_ingredient,
    user_meal,
    user_preference,
    user_preference_threshold,
    user_recipe,
)
from nutrition_tracker.utils import planner as planner_utils


def setup_food_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    foods: list[user_ingredient.UserIngredient] | list[user_recipe.UserRecipe],
    food_preferences: list[user_preference.UserPreference],
    today_meals: list[user_meal.UserMeal],
    object_type_id: int,
    portion: int = 1,
) -> None:
    """Setup food constraints."""
    for food in foods:
        quantity_variable: str = planner_utils.get_quantity_variable(food.external_id)
        presence_variable: str = planner_utils.get_presence_variable(food.external_id)

        variables[presence_variable] = model.NewBoolVar(presence_variable)
        variables[quantity_variable] = model.NewIntVar(
            constants.INT_MIN_VALUE, constants.INT_MAX_VALUE, quantity_variable
        )

        model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])
        model.AddModuloEquality(0, variables[quantity_variable], portion)

        size_from_history: int = _setup_history_constraints(model, variables, food, today_meals, object_type_id)

        _setup_available_quantity_constraints(model, variables, food, object_type_id)

        food_preference: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
            food_preferences, food_external_id=food.external_id
        )
        if not food_preference:
            continue

        _setup_preference_constraints(model, variables, food, food_preference, size_from_history, portion)


def _setup_history_constraints(
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    today_meals: list[user_meal.UserMeal],
    object_type_id: int,
) -> int:
    """Setup history constraints."""
    quantity_variable: str = planner_utils.get_quantity_variable(food.external_id)
    history_size: float | None = food_portion.get_serving_size_in_meals(today_meals, food, object_type_id)
    serving_size_from_history: int = round(history_size or 0)
    model.Add(variables[quantity_variable] >= serving_size_from_history)
    return serving_size_from_history


def _setup_available_quantity_constraints(
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    object_type_id: int,
) -> None:
    """Setup available quantity constraints for recipes."""
    if object_type_id == data_loaders.get_content_type_recipe_id():
        quantity_variable: str = planner_utils.get_quantity_variable(food.external_id)
        model.Add(variables[quantity_variable] <= round(food.portions[0].serving_size))  # type: ignore


def _setup_preference_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    food_preference: user_preference.UserPreference,
    size_from_history: int,
    portion: int,
) -> None:
    """Setup food constraints based on user preferences."""
    presence_variable: str = planner_utils.get_presence_variable(food.external_id)

    if food_preference.is_not_allowed():
        model.Add(variables[presence_variable] == 0)
    else:
        if food_preference.is_not_zeroable():
            model.Add(variables[presence_variable] == 1)

        _setup_threshold_constraints(model, variables, food, food_preference, size_from_history, portion)


def _setup_threshold_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    food_preference: user_preference.UserPreference,
    size_from_history: int,
    portion: int,
) -> None:
    """Setup user preference threshold constraints."""
    _setup_quantity_threshold_constraints(model, variables, food, food_preference, size_from_history, portion)
    _setup_count_threshold_constraints(model, variables, food, food_preference)


def _setup_quantity_threshold_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    food_preference: user_preference.UserPreference,
    size_from_history: int,
    portion: int,
) -> None:
    """Setup user preference threshold quantity constraints."""
    quantity_variable: str = planner_utils.get_quantity_variable(food.external_id)
    presence_variable: str = planner_utils.get_presence_variable(food.external_id)

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(food_preference.userpreferencethreshold_set.all()), dimension=constants.Dimension.QUANTITY, days=1
    )

    if food_preference.is_not_zeroable() or size_from_history:
        if threshold:
            common_planner.setup_threshold_constraint_base(
                model, variables, quantity_variable, food.external_id, threshold, history=size_from_history
            )
        else:
            common_planner.setup_default_food_constraints(
                model, variables, quantity_variable, history=size_from_history
            )
    else:
        intervals: list[list] = [[0]]
        intervals.extend(common_planner.get_threshold_intervals(food_preference, threshold))
        variables[quantity_variable] = model.NewIntVarFromDomain(
            cp_model.Domain.FromIntervals(intervals), quantity_variable
        )
        model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])
        model.AddModuloEquality(0, variables[quantity_variable], portion)


def _setup_count_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    food: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    food_preference: user_preference.UserPreference,
) -> None:
    """Setup user preference threshold count constraints."""
    presence_variable: str = planner_utils.get_presence_variable(food.external_id)

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(food_preference.userpreferencethreshold_set.all()), dimension=constants.Dimension.COUNT, days=1
    )

    if threshold:
        common_planner.setup_threshold_constraint_base(
            model, variables, presence_variable, food.external_id, threshold
        )
