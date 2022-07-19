"""Mealplan logic module."""
from __future__ import annotations

import dataclasses
import random
from typing import Any, Sequence
from uuid import UUID

from django.utils import timezone
from ortools.sat.python import cp_model

import users.models as user_model
from nutrition_tracker.config import usda_config
from nutrition_tracker.logic import data_loaders, food_nutrient, user_prefs
from nutrition_tracker.logic.planner import category as category_planner
from nutrition_tracker.logic.planner import common as common_planner
from nutrition_tracker.logic.planner import food as food_planner
from nutrition_tracker.logic.planner import nutrition as nutrition_planner
from nutrition_tracker.models import (
    db_food_nutrient,
    user_food_nutrient,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)
from nutrition_tracker.utils import planner as planner_utils

MAX_TIME_IN_SECONDS = 5


@dataclasses.dataclass
class Mealplan:
    """Computed mealplan container."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        infeasible: bool,
        lfoods: list[user_ingredient.UserIngredient],
        lrecipes: list[user_recipe.UserRecipe],
        lmember_recipes: list[user_recipe.UserRecipe],
        lmeals_today: list[user_meal.UserMeal],
        lfoods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
        quantity_map: dict[UUID, float | None],
    ) -> None:
        self.infeasible = infeasible
        self.lfoods = lfoods
        self.lrecipes = lrecipes
        self.lmember_recipes = lmember_recipes
        self.lmeals_today = lmeals_today
        self.lfoods_nutrients = lfoods_nutrients
        self.quantity_map = quantity_map


def get_mealplan_for_user(user: user_model.User) -> Mealplan:  # pylint: disable=too-many-locals
    """Get mealplan for user, based on user food and nutrient preferences."""
    # Read user preferences
    luser_preferences: list[user_preference.UserPreference] = list(user_preference.load_luser_preferences(user))
    lfood_preferences: list[user_preference.UserPreference] = list(
        user_prefs.filter_food_preferences(luser_preferences)
    )
    lcategory_preferences: list[user_preference.UserPreference] = list(
        user_prefs.filter_category_preferences(luser_preferences)
    )
    lnutrient_preferences: list[user_preference.UserPreference] = list(
        user_prefs.filter_nutrient_preferences(luser_preferences)
    )

    # Read user meal history
    lmeals_today: list[user_meal.UserMeal] = list(user_meal.load_lmeals(user, meal_date=timezone.localdate()))
    lmeals_yesterday: list[user_meal.UserMeal] = list(
        user_meal.load_lmeals(user, meal_date=(timezone.localdate() - timezone.timedelta(days=1)))
    )

    # Read available and allowable IDs
    usable_preferences: list[user_preference.UserPreference] = list(
        user_prefs.filter_preferences(
            lfood_preferences,
            flags_set=[user_preference.FLAG_IS_AVAILABLE],
            flags_unset=[user_preference.FLAG_IS_NOT_ALLOWED],
        )
    )
    external_ids: list[UUID] = [fp.food_external_id for fp in usable_preferences if fp.food_external_id]

    # Shuffle IDs, for variety of mealplan solutions.
    # Optimistic shuffle, not sure if this does anything.
    random.shuffle(external_ids)

    # Filter non repeatable IDs
    member_foods: list[user_ingredient.UserIngredient] = list(
        data_loaders.load_lfoods_for_lparents(user, lmeals_yesterday)
    )
    member_recipes: list[user_recipe.UserRecipe] = list(
        data_loaders.load_lrecipes_for_lparents(user, lmeals_yesterday)
    )
    external_ids = list(
        common_planner.restrict_to_repeatable_or_unused(external_ids, lfood_preferences, member_foods, member_recipes)
    )

    # Add items from history
    member_foods = list(data_loaders.load_lfoods_for_lparents(user, lmeals_today))
    member_recipes = list(data_loaders.load_lrecipes_for_lparents(user, lmeals_today))
    external_ids = list(common_planner.add_from_history(external_ids, lmeals_today, member_foods, member_recipes))

    # Read foods
    lfoods: list[user_ingredient.UserIngredient] = list(user_ingredient.load_lfoods(user, external_ids=external_ids))

    # Read recipes
    lrecipes: list[user_recipe.UserRecipe] = list(user_recipe.load_lrecipes(user, external_ids=external_ids))
    lrecipe_foods: list[user_ingredient.UserIngredient] = list(data_loaders.load_lfoods_for_lparents(user, lrecipes))
    lmember_recipes: list[user_recipe.UserRecipe] = list(data_loaders.load_lrecipes_for_lparents(user, lrecipes))

    # Read categories
    lcategories: list[usda_config.USDAFoodCategory] = usda_config.usda_food_categories

    lfoods_dict: dict[UUID, user_ingredient.UserIngredient] = {}
    for lfood in lfoods:
        lfoods_dict[lfood.external_id] = lfood
    for lfood in lrecipe_foods:
        if lfood.external_id not in lfoods_dict:
            lfoods_dict[lfood.external_id] = lfood

    # Read food nutrients
    lfoods_nutrients: Sequence[
        db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient
    ] = food_nutrient.get_foods_nutrients(user, list(lfoods_dict.values()))

    # Initialize CP Model
    variables: dict = {}
    model: cp_model.CpModel = cp_model.CpModel()

    # Setup food constraints
    food_planner.setup_food_constraints(
        model, variables, lfoods, lfood_preferences, lmeals_today, data_loaders.get_content_type_ingredient_id()
    )

    # Setup recipe constraints
    food_planner.setup_food_constraints(
        model, variables, lrecipes, lfood_preferences, lmeals_today, data_loaders.get_content_type_recipe_id()
    )

    # Setup group/category constraints
    category_planner.setup_category_constraints(
        model, variables, lfoods, lcategories, lfood_preferences, lcategory_preferences, lmeals_today
    )

    # Setup nutrition preference constraints
    nutrition_planner.setup_nutrition_constraints(
        model, variables, lfoods, lrecipes, lmember_recipes, lfoods_nutrients, lnutrient_preferences, lmeals_today
    )

    objective: str | int = sum(val for key, val in variables.items() if planner_utils.is_constraint_variable(key))
    model.Maximize(objective)

    solver: cp_model.CpSolver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 10
    solver.parameters.max_time_in_seconds = MAX_TIME_IN_SECONDS
    status = solver.Solve(model)
    return Mealplan(
        status
        in [
            cp_model.UNKNOWN,
            cp_model.MODEL_INVALID,
            cp_model.INFEASIBLE,
        ],
        lfoods,
        lrecipes,
        lmember_recipes,
        lmeals_today,
        lfoods_nutrients,
        _get_mealplan_from_solution(solver, status, variables, lfoods, lrecipes),
    )


def _get_mealplan_from_solution(
    solver: cp_model.CpSolver,
    status: Any,
    variables: dict,
    lfoods: list[user_ingredient.UserIngredient],
    lrecipes: list[user_recipe.UserRecipe],
) -> dict[UUID, float | None]:
    """Get quantity_map from mealplan solution."""
    quantity_map: dict[UUID, float | None] = {}
    if status in [cp_model.MODEL_INVALID, cp_model.INFEASIBLE, cp_model.UNKNOWN]:
        return quantity_map

    for lfood in lfoods:
        presence_variable: str = planner_utils.get_presence_variable(lfood.external_id)
        if not solver.Value(variables[presence_variable]):
            continue

        quantity_variable: str = planner_utils.get_quantity_variable(lfood.external_id)
        if not solver.Value(variables[quantity_variable]):
            continue

        quantity_map[lfood.external_id] = solver.Value(variables[quantity_variable])

    for lrecipe in lrecipes:
        presence_variable = planner_utils.get_presence_variable(lrecipe.external_id)
        if not solver.Value(variables[presence_variable]):
            continue

        quantity_variable = planner_utils.get_quantity_variable(lrecipe.external_id)
        if not solver.Value(variables[quantity_variable]):
            continue

        quantity_map[lrecipe.external_id] = solver.Value(variables[quantity_variable])

    return quantity_map
