"""Food portion logic module."""
from __future__ import annotations

from copy import copy
from typing import Any
from uuid import UUID

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import (
    db_food,
    db_food_portion,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_recipe,
)


def get_default_portion_choices(
    serving_size_unit: constants.ServingSizeUnit = constants.ServingSizeUnit.WEIGHT,
) -> list[tuple[Any, float, int, str, str]]:
    """Get default portion choices."""
    # (ID, gram weight, amount, config_unit, measurement_unit)
    # 'oz' and 'fl oz' are shared with strings in usda_config.measure_units
    if serving_size_unit == constants.ServingSizeUnit.WEIGHT:
        return [
            (constants.HUNDRED_SERVING_ID, 100, 100, constants.ServingSizeUnit.WEIGHT, "g"),
            (constants.ONE_SERVING_ID, 1, 1, constants.ServingSizeUnit.WEIGHT, "g"),
            (constants.ONE_OZ_SERVING_ID, 28.3495, 1, "oz", "oz"),
        ]

    if serving_size_unit == constants.ServingSizeUnit.VOLUME:
        return [
            (constants.HUNDRED_SERVING_ID, 100, 100, constants.ServingSizeUnit.VOLUME, "ml"),
            (constants.ONE_SERVING_ID, 1, 1, constants.ServingSizeUnit.VOLUME, "ml"),
            (constants.ONE_OZ_SERVING_ID, 29.5735, 1, "fl oz", "us_oz"),
        ]

    return []


def get_measure_unit_by_id(id_: int | None) -> usda_config.USDAMeasureUnit | None:
    """Get measure unit by ID."""
    return next((m for m in usda_config.usda_measure_units if m.id_ == id_), None)


def get_measure_unit_by_name(name: str) -> usda_config.USDAMeasureUnit | None:
    """Get measure unit by unit name."""
    return next((m for m in usda_config.usda_measure_units if m.name == name), None)


def get_measure_units_sorted_by_name() -> list[usda_config.USDAMeasureUnit]:
    """Get list of measure units sorted by name."""
    return sorted(usda_config.usda_measure_units, key=lambda x: x.name)


def for_display_portion(food_portion: db_food_portion.DBFoodPortion | user_food_portion.UserFoodPortion) -> str:
    """Formatted food portion for display."""
    measure_unit_id_disallowed: list = [constants.UNDETERMINED_MEASURE_UNIT_ID]
    portion_description_disallowed: list = [constants.PORTION_DESCRIPTION_NOT_SPECIFIED]

    portion: str = ""
    quantity: float = getattr(food_portion, "quantity", None) or 1
    if hasattr(food_portion, "serving_size"):
        suffix: str = f"{round(food_portion.serving_size)}{food_portion.serving_size_unit}"  # type: ignore
    else:
        suffix = f"{round(food_portion.gram_weight * quantity)}{constants.ServingSizeUnit.WEIGHT}"  # type: ignore

    infix: str = ""
    use_prefix: bool = False
    if food_portion.amount:
        display_amount: str = "%.3g" % (food_portion.amount * quantity)  # pylint: disable=consider-using-f-string
        measure_unit: usda_config.USDAMeasureUnit | None = get_measure_unit_by_id(food_portion.measure_unit_id)
        unit_name: str | None = (
            measure_unit.abbreviation or measure_unit.name
            if measure_unit and measure_unit.id_ not in measure_unit_id_disallowed
            else None
        ) or (food_portion.modifier if food_portion.modifier else None)

        if unit_name:
            infix = f"{display_amount} {unit_name}"
        else:
            if (
                food_portion.portion_description
                and food_portion.portion_description not in portion_description_disallowed
            ):
                infix = f"{food_portion.portion_description}"
                use_prefix = True
    else:
        if food_portion.portion_description and food_portion.portion_description not in portion_description_disallowed:
            infix = f"{food_portion.portion_description}"
            use_prefix = True

    prefix = ""
    if quantity != 1 and use_prefix:
        prefix = "%.3g" % quantity  # pylint: disable=consider-using-f-string

    if prefix:
        if infix:
            portion = f"{prefix} ({infix}) ({suffix})"
        else:
            portion = f"{prefix} ({suffix})"
    else:
        if infix:
            portion = f"{infix} ({suffix})"
        else:
            portion = f"{suffix}"

    return portion


def for_display_choices(
    lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe | None,
    cfood: db_food.DBFood | None = None,
) -> list[tuple[UUID, str, float | None, str | None, float | None, float | None]]:
    """ "Formatted portion choices for display."""
    portion_choices: list = []

    if lobject and hasattr(lobject, "portions"):
        for lfood_portion in lobject.portions:  # type: ignore
            display_portion: str = for_display_portion(lfood_portion).lower()
            if display_portion:
                portion_choices.append(
                    (
                        lfood_portion.external_id,
                        display_portion,
                        lfood_portion.serving_size,
                        lfood_portion.serving_size_unit,
                        lfood_portion.servings_per_container,
                        lfood_portion.quantity,
                    )
                )

    if cfood:
        for cfood_portion in cfood.dbfoodportion_set.all():
            display_portion = for_display_portion(cfood_portion).lower()
            if display_portion:
                portion_choices.append(
                    (
                        cfood_portion.external_id,
                        display_portion,
                        cfood_portion.serving_size,
                        cfood_portion.serving_size_unit,
                        cfood_portion.servings_per_container,
                        cfood_portion.quantity,
                    )
                )

    # pick the unit type from the first available choice
    if portion_choices:
        serving_size_unit = portion_choices[0][3]
        default_choices = get_default_portion_choices(serving_size_unit=serving_size_unit)
    else:
        serving_size_unit = constants.ServingSizeUnit.WEIGHT
        default_choices = get_default_portion_choices()

    for default_choice in default_choices:
        display_portion = f"{default_choice[2]}{default_choice[3]}"
        portion_choices.append((default_choice[0], display_portion, default_choice[1], serving_size_unit, None, None))

    return portion_choices


def get_food_member_portion(
    member_portion: user_food_portion.UserFoodPortion,
    food_portions: list[tuple[UUID, str, float | None, str | None, float | None, float | None]],
) -> tuple:
    """Get food member portion and quantity based on a list of food portions."""
    # Use a copy of the object to avoid side affects
    member_portion_copy: user_food_portion.UserFoodPortion = copy(member_portion)

    quantity: float | None = member_portion_copy.quantity
    # Reset serving_size and quantity for display string
    member_portion_copy.serving_size = member_portion_copy.serving_size / (quantity or 1)  # type: ignore
    member_portion_copy.quantity = 1
    display_portion: str = for_display_portion(member_portion_copy)
    member_portion_string: str = display_portion.replace(" ", "").lower()

    for fp_tuple in food_portions:
        food_portion_string: str = fp_tuple[1].replace(" ", "").lower()
        if food_portion_string in member_portion_string:
            return fp_tuple, quantity

    return (), 0


def get_serving_size_in_meals(
    lmeals: list[user_meal.UserMeal],
    lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    object_type_id: int,
) -> float | None:
    """Get total serving size for a food/recipe in a list of meals."""
    return sum(
        sum(
            lmember.portions[0].serving_size
            for lmember in lmeal.members  # type: ignore
            if lobject.id == lmember.child_id and lmember.child_type_id == object_type_id
        )
        for lmeal in lmeals
    )


def get_category_serving_size_in_meals(
    lmeals: list[user_meal.UserMeal], category_lfoods: list[user_ingredient.UserIngredient]
) -> float | None:
    """Get total serving size for foods in a category in a list of meals."""
    return sum(
        get_serving_size_in_meals(lmeals, lfood, data_loaders.get_content_type_ingredient_id())
        for lfood in category_lfoods
    )


def get_category_food_count_in_meals(
    lmeals: list[user_meal.UserMeal], category_lfoods: list[user_ingredient.UserIngredient]
) -> int:
    """Get total food count in a category in a list of meals."""
    meal_food_ids: set[int] = {
        lmember.child_id
        for lmeal in lmeals
        for lmember in lmeal.members  # type: ignore
        if lmember.child_type_id == data_loaders.get_content_type_ingredient_id()
    }
    category_food_ids: set[int] = {lfood.id for lfood in category_lfoods}
    return len(meal_food_ids.intersection(category_food_ids))
