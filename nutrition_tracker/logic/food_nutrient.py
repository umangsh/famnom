"""Food nutrition logic module."""
from __future__ import annotations

import os
from typing import Sequence

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

import users.models as user_model
from nutrition_tracker.config import nutrition as nutrition_config
from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, user_prefs
from nutrition_tracker.models import (
    db_food,
    db_food_nutrient,
    usda_food_nutrient,
    user_food_nutrient,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)


def get_nutrient(nutrient_id: int) -> usda_config.USDANutrient | None:
    """Get USDANutrient for a nutrient_id.
    Match against nutrient_nbr if id_ match fails."""
    for u_nutrient in usda_config.usda_nutrients:
        if u_nutrient.id_ == nutrient_id:
            return u_nutrient

    for u_nutrient in usda_config.usda_nutrients:
        if u_nutrient.nutrient_nbr == str(nutrient_id):
            return u_nutrient

    return None


def get_nutrients(nutrient_ids: list[int]) -> list[usda_config.USDANutrient]:
    """Get USDANutrients for a list of nutrient_ids."""
    nutrients: list[usda_config.USDANutrient] = []
    for nutrient_id in nutrient_ids:
        nutrient: usda_config.USDANutrient | None = get_nutrient(nutrient_id)
        if nutrient:
            nutrients.append(nutrient)

    return nutrients


def for_display(nutrient_id: int) -> str | None:
    """Formatted nutrient name for display."""
    nutrient: usda_config.USDANutrient | None = get_nutrient(nutrient_id)
    if not nutrient:
        return None

    return nutrient.display_name


def for_display_unit(nutrient_id: int) -> str:
    """Formatted nutrient unit name for display."""
    nutrient: usda_config.USDANutrient | None = get_nutrient(nutrient_id)
    if not nutrient:
        return ""

    if not nutrient.unit_name:
        return ""

    if nutrient.unit_name in usda_config.ALTERNATE_UNIT_NAME:
        return usda_config.ALTERNATE_UNIT_NAME[nutrient.unit_name].lower()

    return nutrient.unit_name.lower()


def get_fda_rdi(nutrient_id: int) -> nutrition_config.FDANutrientRDI | None:
    """Get FDA Nutrient RDI object for a given nutrient."""
    return next((obj for obj in nutrition_config.fda_nutrient_rdis if obj.nutrient_id == nutrient_id), None)


def get_rdi_amount(nutrient_preferences: list[user_preference.UserPreference], nutrient_id: int) -> float | None:
    """Get FDA RDI amount for a given nutrient and preferences."""
    if nutrient_preferences:
        nutrient_preference: user_preference.UserPreference | None = user_prefs.filter_preferences_by_id(
            nutrient_preferences, food_nutrient_id=nutrient_id
        )
        if nutrient_preference:
            threshold: float | None = user_prefs.get_threshold_value(nutrient_preference)
            if threshold:
                return threshold

    nutrient_rdi = get_fda_rdi(nutrient_id)
    # Pass in the user profile to select the appropriate
    # RDI value, not just the adult value.
    if nutrient_rdi:
        return nutrient_rdi.adult

    return None


def get_all_aliases_for_nutrient_id(nutrient_id: int) -> list[int]:
    """Get all alternative nutrient_ids for a given nutrient ID."""
    aliases: list[int] = []

    nutrient: usda_config.USDANutrient | None = get_nutrient(nutrient_id)
    if not nutrient:
        return aliases

    aliases.append(nutrient.id_)
    if nutrient.nutrient_nbr and nutrient.nutrient_nbr.isnumeric():
        aliases.append(int(nutrient.nutrient_nbr))

    for equivalent_nutrients in usda_config.EQUIVALENT_NUTRIENTS:
        if nutrient.id_ not in equivalent_nutrients:
            continue

        alternate_nutrient_ids: set[int] = set(equivalent_nutrients) - set({nutrient.id_})
        if not alternate_nutrient_ids:
            continue

        for alternate_nutrient_id in alternate_nutrient_ids:
            alternate_nutrient = get_nutrient(alternate_nutrient_id)
            if not alternate_nutrient:
                continue

            aliases.append(alternate_nutrient.id_)
            if alternate_nutrient.nutrient_nbr and alternate_nutrient.nutrient_nbr.isnumeric():
                aliases.append(int(alternate_nutrient.nutrient_nbr))

    return aliases


def get_all_aliases_for_nutrient_ids(nutrient_ids: list[int]) -> list[int]:
    """Get all alternative nutrient_ids for a list of nutrient IDs."""
    aliases: list[int] = []
    for nutrient_id in nutrient_ids:
        aliases.extend(get_all_aliases_for_nutrient_id(nutrient_id))

    return aliases


def get_nutrient_amount(
    food_nutrients: Sequence[
        (usda_food_nutrient.USDAFoodNutrient | db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient)
    ],
    nutrient_id: int,
) -> float | None:
    """Get nutrient amount from a list of food_nutrients."""
    aliases: list[int] = get_all_aliases_for_nutrient_id(nutrient_id)
    if not aliases:
        return None

    return next(
        (food_nutrient.amount for food_nutrient in food_nutrients if food_nutrient.nutrient_id in aliases), None
    )


def get_food_nutrients(
    lfood: user_ingredient.UserIngredient | None, cfood: db_food.DBFood | None
) -> Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient]:
    """Get food nutrients."""
    if lfood and lfood.user:
        return get_foods_nutrients(lfood.user, [lfood])
    if cfood:
        return list(cfood.dbfoodnutrient_set.all())

    return []


def get_foods_nutrients(
    luser: user_model.User, lfoods: list[user_ingredient.UserIngredient], nutrient_id: int | None = None
) -> Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient]:
    """Get food nutrients for a list of foods."""
    aliases: list[int] = []
    if nutrient_id:
        aliases = get_all_aliases_for_nutrient_id(nutrient_id)
        if not aliases:
            return []

    if lfoods:
        lfoods_nutrients: list[user_food_nutrient.UserFoodNutrient] = list(
            user_food_nutrient.load_nutrients(luser, ingredients=lfoods, nutrient_ids=aliases)
        )
    else:
        lfoods_nutrients = []

    db_food_ids = [lfood.db_food_id for lfood in lfoods if lfood.db_food_id]
    if db_food_ids:
        cfoods_nutrients: list[db_food_nutrient.DBFoodNutrient] = list(
            db_food_nutrient.load_nutrients(
                db_food_ids=[lfood.db_food_id for lfood in lfoods if lfood.db_food_id], nutrient_ids=aliases
            )
        )
    else:
        cfoods_nutrients = []

    nutrients: list[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient] = []
    for lfood in lfoods:
        nutrient_id_set: set[int] = set()
        for lfood_nutrient in lfoods_nutrients:
            if lfood_nutrient.ingredient_id == lfood.id and lfood_nutrient.nutrient_id is not None:
                nutrient_id_set.add(lfood_nutrient.nutrient_id)
                nutrients.append(lfood_nutrient)

        for cfood_nutrient in cfoods_nutrients:
            if cfood_nutrient.db_food_id == lfood.db_food_id and cfood_nutrient.nutrient_id not in nutrient_id_set:
                nutrients.append(cfood_nutrient)

    return nutrients


def _is_nutrient_for_food(
    lfood: user_ingredient.UserIngredient,
    food_nutrient: db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient,
) -> bool:
    """Returns true if the food_nutrient belongs to lfood."""
    return (hasattr(food_nutrient, "ingredient_id") and lfood.id == food_nutrient.ingredient_id) or (  # type: ignore
        hasattr(food_nutrient, "db_food_id") and lfood.db_food_id == food_nutrient.db_food_id  # type: ignore
    )


def get_nutrient_amount_in_foods(
    lfoods: list[user_ingredient.UserIngredient],
    lfoods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
    nutrient_id: int,
) -> float | None:
    """Get nutrient amount for a given nutrient ID in a list of foods."""
    aliases: list[int] = get_all_aliases_for_nutrient_id(nutrient_id)
    if not aliases:
        return None

    nutrients: list[float | None] = [
        next(
            (
                lfood_nutrient.amount
                for lfood_nutrient in lfoods_nutrients
                if lfood_nutrient.nutrient_id in aliases and _is_nutrient_for_food(lfood, lfood_nutrient)
            ),
            None,
        )
        for lfood in lfoods
    ]

    if all(nutrient is None for nutrient in nutrients):
        return None

    return sum(filter(None, nutrients))


def get_nutrient_amount_in_lparents(
    lparents: list[user_recipe.UserRecipe] | list[user_meal.UserMeal] | list,
    lfoods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
    nutrient_id: int,
    member_recipes: list[user_recipe.UserRecipe] | None = None,
) -> float | None:
    """Get nutrient amount for a given nutrient ID in a list of recipes/meals."""
    if not member_recipes:
        member_recipes = []

    nutrients: list[float | None] = []
    for lparent in lparents:
        for lparent_member in lparent.members:  # type: ignore
            if lparent_member.child_type_id == data_loaders.get_content_type_ingredient_id():
                nutrient: float | None = get_nutrient_amount_in_foods(
                    [lparent_member.child], lfoods_nutrients, nutrient_id
                )
            elif lparent_member.child_type_id == data_loaders.get_content_type_recipe_id():
                lrecipe: user_recipe.UserRecipe | None = next(
                    (lrecipe for lrecipe in member_recipes if lrecipe.id == lparent_member.child_id), None
                )
                nutrient = get_nutrient_amount_in_lparents(
                    [lrecipe] if lrecipe else [], lfoods_nutrients, nutrient_id, member_recipes=member_recipes
                )

            if nutrient:
                if hasattr(lparent, "portions") and lparent.portions:  # type: ignore
                    serving_size: float | None = lparent.portions[0].serving_size  # type: ignore
                else:
                    serving_size = constants.PORTION_SIZE

                nutrients.append(lparent_member.portions[0].serving_size * nutrient / serving_size)

    if not nutrients:
        return None

    return sum(nutrients)


def get_nutrient_amount_in_mealplan(  # pylint: disable=too-many-arguments
    lfoods: list[user_ingredient.UserIngredient],
    lrecipes: list[user_recipe.UserRecipe],
    quantity_map: dict,
    lfoods_nutrients: Sequence[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient],
    nutrient_id: int,
    member_recipes: list[user_recipe.UserRecipe] | None = None,
) -> float | None:
    """Get nutrient amount for a given nutrient ID in a mealplan."""
    if not member_recipes:
        member_recipes = []

    nutrients: list[float | None] = []
    for lfood in lfoods:
        if lfood.external_id not in quantity_map:
            continue

        nutrient: float | None = get_nutrient_amount_in_foods([lfood], lfoods_nutrients, nutrient_id)
        if nutrient:
            serving_size: float = quantity_map.get(lfood.external_id, 0)
            nutrients.append(serving_size * nutrient / constants.PORTION_SIZE)

    for lrecipe in lrecipes:
        if lrecipe.external_id not in quantity_map:
            continue

        nutrient = get_nutrient_amount_in_lparents(
            [lrecipe], lfoods_nutrients, nutrient_id, member_recipes=member_recipes
        )
        if nutrient:
            serving_size = quantity_map.get(lrecipe.external_id, 0)
            nutrients.append(serving_size * nutrient / constants.PORTION_SIZE)

    if not nutrients:
        return None

    return sum(nutrients)


def get_recent_foods_for_nutrient(
    luser: user_model.User, nutrient_id: int, max_items: int = 10, max_meals: int = 10
) -> list[user_ingredient.UserIngredient]:
    """Get recent foods containing the given nutrient_id. The resulting list is ordered by nutrient amount in descending order."""
    recent_lfoods: list[user_ingredient.UserIngredient] = []
    lnutrient = get_nutrient(nutrient_id)
    if not lnutrient:
        return recent_lfoods

    lmeals = list(user_meal.load_lmeals(luser, order_by="-meal_date", max_rows=max_meals))
    lfoods = list(data_loaders.load_lfoods_for_lparents(luser, lmeals))
    lfoods_nutrients = get_foods_nutrients(luser, lfoods, nutrient_id=nutrient_id)
    lfoods_nutrients = sorted(lfoods_nutrients, key=lambda x: x.amount, reverse=True)  # type: ignore

    for lfn in lfoods_nutrients:
        if not lfn.amount:
            continue

        if hasattr(lfn, "ingredient"):
            lfood = next((lfood for lfood in lfoods if lfood == lfn.ingredient), None)  # type: ignore
        else:
            lfood = next((lfood for lfood in lfoods if lfood.db_food == lfn.db_food), None)  # type: ignore

        if lfood and lfood not in recent_lfoods:
            recent_lfoods.append(lfood)
            if len(recent_lfoods) == max_items:
                return recent_lfoods

    return recent_lfoods


def get_top_cfoods_for_nutrient(nutrient_id: int) -> list[db_food.DBFood]:
    """Get top foods containing the given nutrient_id."""
    top_foods_prefix = (
        f"{os.getcwd()}/nutrition_tracker/generated/top_foods/{'dev' if settings.DJANGO_ENV == 'dev' else 'prod'}/"
    )
    cache_key: str = f"top_foods:{nutrient_id}"
    external_ids: list = cache.get(cache_key, [])
    if not external_ids:
        filepath = f"{top_foods_prefix}{nutrient_id}.txt"
        if os.path.exists(filepath):
            with open(filepath, encoding="utf8") as file_:
                external_ids = file_.read().splitlines()
                if external_ids:
                    cache.set(cache_key, external_ids)

    return list(db_food.load_cfoods(external_ids=external_ids))


def get_tracker_nutrients(luser: user_model.User, nutrient_id: int, total_days: int = 5) -> dict:
    """Returns a (date, nutrient amount) map for the last total_days from current date."""
    lmeals = list(user_meal.load_lmeals(luser, meal_date=timezone.localdate(), num_days=total_days))
    lfoods = list(data_loaders.load_lfoods_for_lparents(luser, lmeals))
    member_recipes = list(data_loaders.load_lrecipes_for_lparents(luser, lmeals))
    foods_nutrients = get_foods_nutrients(luser, lfoods, nutrient_id=nutrient_id)

    response = {}
    for days in reversed(range(total_days)):
        current_date = timezone.localdate() - timezone.timedelta(days=days)
        current_lmeals = [lmeal for lmeal in lmeals if lmeal.meal_date == current_date]
        nutrient_value = get_nutrient_amount_in_lparents(
            current_lmeals, foods_nutrients, nutrient_id, member_recipes=member_recipes
        )
        response[current_date] = nutrient_value

    return response
