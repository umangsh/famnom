"""Nutrition logic module for mealplanning."""
from __future__ import annotations

from typing import Sequence

from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient, user_prefs
from nutrition_tracker.logic.planner import common as common_planner
from nutrition_tracker.models import (
    db_food_nutrient,
    user_food_nutrient,
    user_ingredient,
    user_meal,
    user_preference,
    user_preference_threshold,
    user_recipe,
)
from nutrition_tracker.utils import planner as planner_utils


def setup_nutrition_constraints(  # pylint: disable=too-many-arguments
    model: cp_model.CpModel,
    variables: dict,
    foods: list[user_ingredient.UserIngredient],
    recipes: list[user_recipe.UserRecipe],
    member_recipes: list[user_recipe.UserRecipe],
    foods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
    nutrient_preferences: list[user_preference.UserPreference],
    today_meals: list[user_meal.UserMeal],
) -> None:
    """Setup nutrition constraints."""
    for nutrient_preference in nutrient_preferences:
        if nutrient_preference.is_not_allowed():
            continue

        if not nutrient_preference.food_nutrient_id:
            continue

        nutrient_id: int = nutrient_preference.food_nutrient_id
        multiplier: int = constants.SCALING_FACTOR * constants.PORTION_SIZE
        quantity_variable: str = planner_utils.get_quantity_variable(nutrient_id)
        presence_variable: str = planner_utils.get_presence_variable(nutrient_id)

        variables[presence_variable] = model.NewBoolVar(presence_variable)
        variables[quantity_variable] = model.NewIntVar(
            constants.INT_MIN_VALUE, constants.INT_MAX_VALUE * multiplier, quantity_variable
        )

        model.Add(variables[quantity_variable] == 0).OnlyEnforceIf(variables[presence_variable].Not())
        model.Add(variables[quantity_variable] > 0).OnlyEnforceIf(variables[presence_variable])
        model.Add(
            sum(
                [
                    sum(
                        variables[planner_utils.get_quantity_variable(food.external_id)]
                        * round(
                            (
                                food_nutrient.get_nutrient_amount_in_foods(
                                    [food], foods_nutrients, nutrient_preference.food_nutrient_id
                                )
                                or 0
                            )
                            * constants.SCALING_FACTOR
                        )
                        for food in foods
                    ),
                    sum(
                        variables[planner_utils.get_quantity_variable(recipe.external_id)]
                        * round(
                            (
                                food_nutrient.get_nutrient_amount_in_lparents(
                                    [recipe],
                                    foods_nutrients,
                                    nutrient_preference.food_nutrient_id,
                                    member_recipes=member_recipes,
                                )
                                or 0
                            )
                            * constants.SCALING_FACTOR
                        )
                        for recipe in recipes
                    ),
                ]
            )
            == variables[quantity_variable]
        )

        _setup_history_constraints(model, variables, foods_nutrients, nutrient_id, today_meals)
        _setup_preference_constraints(model, variables, nutrient_preference)


def _setup_history_constraints(
    model: cp_model.CpModel,
    variables: dict,
    foods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
    nutrient_id: int,
    today_meals: list[user_meal.UserMeal],
) -> None:
    """Setup history constraints."""
    history_size: float | None = food_nutrient.get_nutrient_amount_in_lparents(
        today_meals, foods_nutrients, nutrient_id
    )
    nutrient_amount_from_history: float = history_size or 0
    multiplier: int = constants.SCALING_FACTOR * constants.PORTION_SIZE
    quantity_variable: str = planner_utils.get_quantity_variable(nutrient_id)
    model.Add(variables[quantity_variable] >= round(multiplier * nutrient_amount_from_history))


def _setup_preference_constraints(
    model: cp_model.CpModel, variables: dict, nutrient_preference: user_preference.UserPreference
) -> None:
    """Setup user preference constraints."""
    if not nutrient_preference.food_nutrient_id:
        return

    threshold: user_preference_threshold.UserPreferenceThreshold | None = user_prefs.filter_preference_thresholds(
        list(nutrient_preference.userpreferencethreshold_set.all()), dimension=constants.Dimension.QUANTITY, days=1
    )

    if threshold:
        nutrient_id: int = nutrient_preference.food_nutrient_id
        multiplier: int = constants.SCALING_FACTOR * constants.PORTION_SIZE
        quantity_variable: str = planner_utils.get_quantity_variable(nutrient_id)
        enforce_exact: bool = nutrient_id == constants.ENERGY_NUTRIENT_ID
        common_planner.setup_threshold_constraint_base(
            model,
            variables,
            quantity_variable,
            nutrient_id,
            threshold,
            multiplier=multiplier,
            enforce_exact=enforce_exact,
        )
