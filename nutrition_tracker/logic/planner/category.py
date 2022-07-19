"""Category logic module for mealplanning."""
from __future__ import annotations

from ortools.sat.python import cp_model

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion, user_prefs
from nutrition_tracker.logic.planner import common as common_planner
from nutrition_tracker.models import user_ingredient, user_meal, user_preference, user_preference_threshold
from nutrition_tracker.utils import planner as planner_utils


def setup_category_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    foods: list[user_ingredient.UserIngredient],
    categories: list[usda_config.USDAFoodCategory],
    food_preferences: list[user_preference.UserPreference],
    category_preferences: list[user_preference.UserPreference],
    today_meals: list[user_meal.UserMeal],
) -> None:
    """Setup category constraints."""
    for category in categories:
        category_preference: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
            category_preferences, food_category_id=category.id_
        )

        if not category_preference:
            continue

        if category.id_ == constants.CATEGORY_ALL_FOODS:
            category_foods: list[user_ingredient.UserIngredient] = foods
        else:
            category_foods = [lfood for lfood in foods if lfood.category_id == category.id_]

        quantity_variable: str = planner_utils.get_quantity_variable(category.id_)
        presence_variable: str = planner_utils.get_presence_variable(category.id_)
        sum_variable: str = planner_utils.get_sum_variable(category.id_)

        variables[presence_variable] = model.NewBoolVar(presence_variable)
        variables[quantity_variable] = model.NewIntVar(
            constants.INT_MIN_VALUE, constants.INT_MAX_VALUE, quantity_variable
        )
        variables[sum_variable] = model.NewIntVar(constants.INT_MIN_VALUE, constants.INT_MAX_VALUE, sum_variable)

        model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])
        model.Add(
            sum(variables[planner_utils.get_quantity_variable(food.external_id)] for food in category_foods)
            == variables[quantity_variable]
        )

        model.Add(variables[sum_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[sum_variable] > 0).OnlyEnforceIf(variables[presence_variable])
        model.Add(
            sum(variables[planner_utils.get_presence_variable(food.external_id)] for food in category_foods)
            == variables[sum_variable]
        )

        _setup_history_constraints(model, variables, category, category_foods, today_meals)
        _setup_preference_constraints(
            model, variables, category, category_foods, category_preference, food_preferences
        )


def _setup_history_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_foods: list[user_ingredient.UserIngredient],
    today_meals: list[user_meal.UserMeal],
) -> None:
    quantity_variable: str = planner_utils.get_quantity_variable(category.id_)
    sum_variable: str = planner_utils.get_sum_variable(category.id_)

    history_size: float | None = food_portion.get_category_serving_size_in_meals(today_meals, category_foods)
    category_serving_size_from_history: int = round(history_size or 0)
    category_food_count_from_history: int = food_portion.get_category_food_count_in_meals(today_meals, category_foods)
    model.Add(variables[quantity_variable] >= category_serving_size_from_history)
    model.Add(variables[sum_variable] >= category_food_count_from_history)


def _setup_preference_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_foods: list[user_ingredient.UserIngredient],
    category_preference: user_preference.UserPreference,
    food_preferences: list[user_preference.UserPreference],
) -> None:
    """Setup category constraints based on user preferences."""
    presence_variable: str = planner_utils.get_presence_variable(category.id_)

    if category_preference.is_not_allowed():
        model.Add(variables[presence_variable] == 0)
    else:
        if category_preference.is_not_zeroable():
            model.Add(variables[presence_variable] == 1)

        _setup_threshold_constraints(model, variables, category, category_foods, category_preference, food_preferences)


def _setup_threshold_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_foods: list[user_ingredient.UserIngredient],
    category_preference: user_preference.UserPreference,
    food_preferences: list[user_preference.UserPreference],
) -> None:
    """Setup user preference threshold constraints."""
    _setup_quantity_threshold_constraints(
        model, variables, category, category_foods, category_preference, food_preferences
    )
    _setup_count_threshold_constraints(model, variables, category, category_preference)


def _setup_quantity_threshold_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_foods: list[user_ingredient.UserIngredient],
    category_preference: user_preference.UserPreference,
    food_preferences: list[user_preference.UserPreference],
) -> None:
    """Setup user preference threshold quantity constraints."""
    _setup_self_quantity_threshold_constraints(model, variables, category, category_preference)
    _setup_member_quantity_threshold_constraints(
        model, variables, category_foods, category_preference, food_preferences
    )


def _setup_self_quantity_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_preference: user_preference.UserPreference,
) -> None:
    """Setup user preference threshold self quantity constraints."""
    quantity_variable: str = planner_utils.get_quantity_variable(category.id_)
    presence_variable: str = planner_utils.get_presence_variable(category.id_)

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(category_preference.userpreferencethreshold_set.all()),
        dimension=constants.Dimension.QUANTITY,
        days=1,
        expansion_set=constants.ExpansionSet.SELF,
    )

    if category_preference.is_not_zeroable():
        if threshold:
            common_planner.setup_threshold_constraint_base(
                model, variables, quantity_variable, category.id_, threshold
            )
    else:
        intervals: list[list] = [[0]]
        intervals += common_planner.get_threshold_intervals(category_preference, threshold)
        variables[quantity_variable] = model.NewIntVarFromDomain(
            cp_model.Domain.FromIntervals(intervals), quantity_variable
        )
        model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])


def _setup_member_quantity_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category_foods: list[user_ingredient.UserIngredient],
    category_preference: user_preference.UserPreference,
    food_preferences: list[user_preference.UserPreference],
) -> None:
    """Setup user preference threshold member quantity constraints."""
    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(category_preference.userpreferencethreshold_set.all()),
        dimension=constants.Dimension.QUANTITY,
        days=1,
        expansion_set=constants.ExpansionSet.MEMBERS,
    )

    for food in category_foods:
        quantity_variable: str = planner_utils.get_quantity_variable(food.external_id)
        presence_variable: str = planner_utils.get_presence_variable(food.external_id)

        food_preference: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
            food_preferences, food_external_id=food.external_id
        )

        if not food_preference or food_preference.is_not_zeroable():
            if threshold:
                common_planner.setup_threshold_constraint_base(
                    model, variables, quantity_variable, food.external_id, threshold
                )
        else:
            food_threshold = user_prefs.filter_preference_thresholds(
                list(food_preference.userpreferencethreshold_set.all()), dimension=constants.Dimension.QUANTITY, days=1
            )

            intervals: list[list] = [[0]]
            category_interval: list[list] = common_planner.get_threshold_intervals(category_preference, threshold)
            food_interval: list[list] = common_planner.get_threshold_intervals(food_preference, food_threshold)
            intervals += [
                [max(food_interval[0][0], category_interval[0][0]), min(food_interval[0][1], category_interval[0][1])]
            ]
            variables[quantity_variable] = model.NewIntVarFromDomain(
                cp_model.Domain.FromIntervals(intervals), quantity_variable
            )
            model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
            model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])


def _setup_count_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_preference: user_preference.UserPreference,
) -> None:
    """Setup user preference threshold count constraints."""
    _setup_self_count_threshold_constraints(model, variables, category, category_preference)
    _setup_member_count_threshold_constraints(model, variables, category, category_preference)


def _setup_self_count_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory,
    category_preference: user_preference.UserPreference,
) -> None:
    """Setup user preference threshold self count constraints."""
    presence_variable: str = planner_utils.get_presence_variable(category.id_)

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(category_preference.userpreferencethreshold_set.all()),
        dimension=constants.Dimension.COUNT,
        days=1,
        expansion_set=constants.ExpansionSet.SELF,
    )

    if threshold:
        common_planner.setup_threshold_constraint_base(model, variables, presence_variable, category.id_, threshold)


def _setup_member_count_threshold_constraints(
    model: cp_model.CpModel,
    variables: dict,
    category: usda_config.USDAFoodCategory | usda_config.WWEIAFoodCategory,
    category_preference: user_preference.UserPreference,
) -> None:
    """Setup user preference threshold member count constraints."""
    sum_variable: str = planner_utils.get_sum_variable(category.id_)

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(category_preference.userpreferencethreshold_set.all()),
        dimension=constants.Dimension.COUNT,
        days=1,
        expansion_set=constants.ExpansionSet.MEMBERS,
    )

    if threshold:
        common_planner.setup_threshold_constraint_base(model, variables, sum_variable, category.id_, threshold)
