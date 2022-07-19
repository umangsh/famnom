"""Utility template tags for nutrition_tracker templates."""
from __future__ import annotations

import uuid
from typing import Any
from urllib.parse import urlencode

from django import template
from django.conf import settings

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_category, food_nutrient, food_portion, user_prefs
from nutrition_tracker.models import (
    db_food,
    db_food_nutrient,
    db_food_portion,
    user_food_nutrient,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)

register = template.Library()


def _highlight_base(path: str, paths: list[str]) -> bool:
    """Check if the prefix string in path appears in a list of strings paths."""
    (prefix, _, _) = path.strip("/").partition("/")
    return any(p == prefix for p in paths)


def _get_lfood_cfood_from_context(
    context: dict, lfood_id: int | None = None
) -> tuple[user_ingredient.UserIngredient | None, db_food.DBFood | None]:
    """Return lfood and cfood objects from context, if they exist."""
    if lfood_id:
        lfoods: list[user_ingredient.UserIngredient] = context.get("lfoods", [])
        lfood: user_ingredient.UserIngredient | None = next((lfood for lfood in lfoods if lfood_id == lfood.id), None)
        if lfood:
            cfoods: list[db_food.DBFood] = context.get("cfoods", [])
            cfood: db_food.DBFood | None = next((cfood for cfood in cfoods if cfood.id == lfood.db_food_id), None)

    if not lfood_id or not lfood:
        lfood = context.get("lfood")

    if not lfood_id or not cfood:
        cfood = context.get("cfood")

    return lfood, cfood


def _get_lrecipe_from_context(context: dict, lrecipe_id: int | None = None) -> user_recipe.UserRecipe | None:
    """Return lrecipe object from context, if it exists."""
    if lrecipe_id:
        lrecipes: list[user_recipe.UserRecipe] = context.get("lrecipes", [])
        lrecipe: user_recipe.UserRecipe | None = next(
            (lrecipe for lrecipe in lrecipes if lrecipe_id == lrecipe.id), None
        )

        if not lrecipe:
            member_recipes: list[user_recipe.UserRecipe] = context.get("member_recipes", [])
            lrecipe = next((member_recipe for member_recipe in member_recipes if lrecipe_id == member_recipe.id), None)

    if not lrecipe_id or not lrecipe:
        lrecipe = context.get("lrecipe")

    return lrecipe


@register.filter
def get_item(dictionary: dict, key: Any) -> Any:
    """Dictionary lookup templatetag."""
    return dictionary.get(key)


@register.filter
def get_classname(obj: object) -> str:
    """Get classname for the given object."""
    return obj.__class__.__name__


@register.simple_tag
def settings_value(name: str) -> str | Any:
    """Return settings.<name> if exists, "" otherwise."""
    return getattr(settings, name, "")


@register.simple_tag
def get_content_type_ingredient_id() -> int:
    """Return user_ingredient content type ID."""
    return data_loaders.get_content_type_ingredient_id()


@register.simple_tag
def get_content_type_recipe_id() -> int:
    """Return user_recipe content type ID."""
    return data_loaders.get_content_type_recipe_id()


@register.simple_tag
def get_content_type_meal_id() -> int:
    """Return user_meal content type ID."""
    return data_loaders.get_content_type_meal_id()


@register.simple_tag(takes_context=True)
def normalize_portion_size(context: dict, value: float | None) -> float | None:
    """Normalize nutrient values to portion size. Nutrients are stored per constants.PORITONS_SIZE, scale the value for default_serving_size."""
    if not value:
        return value

    default_portion: None | (
        tuple[uuid.UUID, str, float | None, str | None, float | None, float | None]
    ) = context.get("default_portion")
    if not default_portion:
        return value

    default_serving_size: float | None = default_portion[2]
    if not default_serving_size:
        return value

    default_portion_quantity = context.get("default_portion_quantity") or 1
    return value * default_serving_size * default_portion_quantity / constants.PORTION_SIZE


@register.filter
def display_nutrient_name(nutrient_id: int) -> str | None:
    """Formatted nutrient name for display."""
    return food_nutrient.for_display(nutrient_id)


@register.filter
def display_nutrient_unit(nutrient_id: int) -> str:
    """Formatted nutrient unit name for display."""
    return food_nutrient.for_display_unit(nutrient_id)


@register.filter
def display_portion(portion: db_food_portion.DBFoodPortion | user_food_portion.UserFoodPortion) -> str:
    """Formatted portion value for display."""
    return food_portion.for_display_portion(portion).lower()


@register.simple_tag(takes_context=True)
def display_food_name(context: dict, lfood_id: int | None = None) -> str:
    """Formatted food name for display."""
    lfood, cfood = _get_lfood_cfood_from_context(context, lfood_id=lfood_id)
    if lfood:
        return lfood.display_name or ""

    if cfood:
        return cfood.display_name or ""

    return ""


@register.simple_tag(takes_context=True)
def display_brand_field(context: dict, fieldname: str, lfood_id: int | None = None) -> str:
    """Formatted brand field for display."""
    lfood, cfood = _get_lfood_cfood_from_context(context, lfood_id=lfood_id)
    if lfood:
        return lfood.display_brand_field(fieldname) or ""

    if cfood:
        return cfood.display_brand_field(fieldname) or ""

    return ""


@register.filter
def display_category_name(category_id: int) -> str | None:
    """Formatted category name for display."""
    return food_category.for_display(category_id)


@register.simple_tag(takes_context=True)
def display_brand_details(context: dict, lfood_id: int | None = None) -> str:
    """Formatted brand details for display."""
    lfood, cfood = _get_lfood_cfood_from_context(context, lfood_id=lfood_id)
    if lfood:
        return lfood.display_brand_details or ""

    if cfood:
        return cfood.display_brand_details or ""

    return ""


@register.simple_tag(takes_context=True)
def display_recipe_name(context: dict, lrecipe_id: int | None = None, with_date: bool = True) -> str:
    """Formatted recipe name for display."""
    lrecipe = _get_lrecipe_from_context(context, lrecipe_id=lrecipe_id)
    if not lrecipe:
        return ""

    return lrecipe.display_name(with_date=with_date) or ""


@register.simple_tag(takes_context=True)
def display_recipe_date(context: dict, lrecipe_id: int | None = None) -> str:
    """Formatted recipe date for display."""
    lrecipe = _get_lrecipe_from_context(context, lrecipe_id=lrecipe_id)
    if not lrecipe:
        return ""

    return lrecipe.display_date


@register.simple_tag
def get_threshold_value(luser_preference: user_preference.UserPreference | None) -> float | None:
    """Get user preference threshold value."""
    if not luser_preference:
        return None

    return user_prefs.get_threshold_value(luser_preference)


@register.simple_tag(takes_context=True)
def get_nutrient_amount(  # pylint: disable=too-many-return-statements
    context: dict, nutrient_id: int, type_: int | None = 0
) -> float | None:
    """Get formatted nutrient amount for display."""
    food_nutrients: list[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient] = context.get(
        "food_nutrients", []
    )
    if not food_nutrients:
        return None

    lmeals: list[user_meal.UserMeal] = context.get("lmeals", [])
    lmeal: user_meal.UserMeal | None = context.get("lmeal")
    lrecipes: list[user_recipe.UserRecipe] = context.get("lrecipes", [])
    member_recipes: list[user_recipe.UserRecipe] = context.get("member_recipes", [])
    lrecipe: user_recipe.UserRecipe | None = context.get("lrecipe")
    lfoods: list[user_ingredient.UserIngredient] = context.get("lfoods", [])
    lfood: user_ingredient.UserIngredient = context.get("lfood", None)
    quantity_map: dict = context.get("quantity_map", {})

    if type_ == constants.MEALPLAN_NUTRIENTS:
        return food_nutrient.get_nutrient_amount_in_mealplan(
            lfoods, lrecipes, quantity_map, food_nutrients, nutrient_id, member_recipes=member_recipes
        )

    if type_ == constants.MEALS_NUTRIENTS:
        return food_nutrient.get_nutrient_amount_in_lparents(
            lmeals, food_nutrients, nutrient_id, member_recipes=member_recipes
        )

    if type_ == constants.MEAL_NUTRIENTS and lmeal:
        return food_nutrient.get_nutrient_amount_in_lparents(
            [lmeal], food_nutrients, nutrient_id, member_recipes=member_recipes
        )

    if type_ == constants.RECIPE_NUTRIENTS and lrecipe:
        return food_nutrient.get_nutrient_amount_in_lparents(
            [lrecipe], food_nutrients, nutrient_id, member_recipes=member_recipes
        )

    if type_ == constants.FOODS_NUTRIENTS:
        return food_nutrient.get_nutrient_amount_in_foods(lfoods, food_nutrients, nutrient_id)

    if type_ == constants.FOOD_NUTRIENTS:
        return food_nutrient.get_nutrient_amount_in_foods([lfood], food_nutrients, nutrient_id)

    return food_nutrient.get_nutrient_amount(food_nutrients, nutrient_id)


@register.simple_tag(takes_context=True)
def get_rdi_amount(context: dict, nutrient_id: int) -> float | None:
    """Formatted FDA RDI nutrient amount based on preferences."""
    nutrient_preferences: list[user_preference.UserPreference] = context.get("nutrient_preferences", [])
    return food_nutrient.get_rdi_amount(nutrient_preferences, nutrient_id)


@register.filter
def highlight_index(path: str) -> bool:
    """Return true for homepage paths."""
    paths: list[str] = [""]
    return _highlight_base(path, paths)


@register.filter
def highlight_search(path: str) -> bool:
    """Return true for search paths."""
    paths: list[str] = constants.SEARCH_URLS
    return _highlight_base(path, paths)


@register.filter
def highlight_mealplan(path: str) -> bool:
    """Return true for mealplan paths."""
    paths: list[str] = constants.MEALPLAN_URLS
    return _highlight_base(path, paths)


@register.filter
def highlight_kitchen(path: str) -> bool:
    """Return true for kitchen paths."""
    return highlight_foods(path) or highlight_recipes(path) or highlight_meals(path)


@register.filter
def highlight_foods(path: str) -> bool:
    """Return true for foods paths."""
    paths: list[str] = constants.FOOD_URLS
    return _highlight_base(path, paths)


@register.filter
def highlight_recipes(path: str) -> bool:
    """Return true for recipes paths."""
    paths: list[str] = constants.RECIPE_URLS
    return _highlight_base(path, paths)


@register.filter
def highlight_meals(path: str) -> bool:
    """Return true for meals paths."""
    paths: list[str] = constants.MEAL_URLS
    return _highlight_base(path, paths)


@register.simple_tag(takes_context=True)
def url_replace(context: dict, **kwargs: Any) -> str:
    """Encode params in **kwargs as a URL. Pop 'page' argument."""
    query: dict = context["request"].GET.copy()
    query.pop("page", None)
    query.update(kwargs)
    return urlencode(query)
