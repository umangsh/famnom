"""Form processing logic module."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from measurement.utils import guess

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion, user_prefs
from nutrition_tracker.models import (
    db_food,
    db_food_portion,
    user_food_portion,
    user_ingredient,
    user_preference,
    user_recipe,
)


def get_portion_choices_form_data(
    lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe, cfood: db_food.DBFood | None = None
) -> Any:
    """Get portion choices for form dropdowns."""
    portion_choices: list[
        tuple[UUID, str, float | None, str | None, float | None, float | None]
    ] = food_portion.for_display_choices(lobject, cfood=cfood)
    return [
        (id_, {"label": display_string, "data-gm-wt": serving_size, "data-wt-unit": serving_size_unit})
        for id_, display_string, serving_size, serving_size_unit, _unused_1, _unused_2 in portion_choices
    ]


def process_portion_choices_form_data(
    quantity: float | None,
    portion: str,
    lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe,
    cfood: db_food.DBFood | None = None,
    lfood_portion: user_food_portion.UserFoodPortion | None = None,
) -> user_food_portion.UserFoodPortion:
    """Process portion choices form dropdown data."""
    if not lfood_portion:
        lfood_portion = user_food_portion.UserFoodPortion()

    _unused, serving_size_unit = get_serving_defaults(lobject)
    default_portions: list[tuple[Any, float, int, str, str]] = food_portion.get_default_portion_choices(
        serving_size_unit=serving_size_unit
    )
    default_portion: tuple[Any, float, int, str, str] | None = next(
        (default_choice for default_choice in default_portions if str(default_choice[0]) == portion), None
    )
    if default_portion:
        measurement = guess(default_portion[2], default_portion[4])
        measure_unit: usda_config.USDAMeasureUnit | None = food_portion.get_measure_unit_by_name(default_portion[3])
        if measurement.__class__.__name__ == "Volume":
            lfood_portion.serving_size = measurement.ml
            lfood_portion.serving_size_unit = constants.ServingSizeUnit.VOLUME
        else:
            lfood_portion.serving_size = measurement.g
            lfood_portion.serving_size_unit = constants.ServingSizeUnit.WEIGHT

        lfood_portion.amount = measurement.value if measure_unit else None
        lfood_portion.measure_unit_id = measure_unit.id_ if measure_unit else None

    else:
        if lobject and hasattr(lobject, "portions") and lobject.portions:  # type: ignore
            lfp: user_food_portion.UserFoodPortion | None = next(
                (lfp for lfp in lobject.portions if str(lfp.external_id) == portion), None  # type: ignore
            )

            if lfp:
                lfood_portion.serving_size = lfp.serving_size
                lfood_portion.serving_size_unit = lfp.serving_size_unit
                lfood_portion.amount = lfp.amount
                lfood_portion.measure_unit_id = lfp.measure_unit_id
                lfood_portion.modifier = lfp.modifier
                lfood_portion.portion_description = lfp.portion_description
            else:
                if not cfood:
                    return lfood_portion

                cfood_portion: db_food_portion.DBFoodPortion | None = next(
                    (
                        cfood_portion
                        for cfood_portion in cfood.dbfoodportion_set.all()
                        if str(cfood_portion.external_id) == portion
                    ),
                    None,
                )
                if cfood_portion:
                    lfood_portion.serving_size = cfood_portion.serving_size
                    lfood_portion.serving_size_unit = cfood_portion.serving_size_unit
                    lfood_portion.amount = cfood_portion.amount
                    lfood_portion.measure_unit_id = cfood_portion.measure_unit_id
                    lfood_portion.modifier = cfood_portion.modifier
                    lfood_portion.portion_description = cfood_portion.portion_description
        else:
            if not cfood:
                return lfood_portion

            cfood_portion = next(
                (
                    cfood_portion
                    for cfood_portion in cfood.dbfoodportion_set.all()
                    if str(cfood_portion.external_id) == portion
                ),
                None,
            )
            if cfood_portion:
                lfood_portion.serving_size = cfood_portion.serving_size
                lfood_portion.serving_size_unit = cfood_portion.serving_size_unit
                lfood_portion.amount = cfood_portion.amount
                lfood_portion.measure_unit_id = cfood_portion.measure_unit_id
                lfood_portion.modifier = cfood_portion.modifier
                lfood_portion.portion_description = cfood_portion.portion_description

    lfood_portion.quantity = quantity
    lfood_portion.serving_size = (lfood_portion.serving_size or 1) * (quantity or 1)
    return lfood_portion


def get_serving_defaults(
    lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe,
) -> tuple[float, constants.ServingSizeUnit]:
    """Get default serving size and unit."""
    serving_size: float = constants.PORTION_SIZE
    serving_size_unit: constants.ServingSizeUnit = constants.ServingSizeUnit.WEIGHT

    if hasattr(lobject, "portions") and lobject.portions:  # type: ignore
        serving_size = lobject.portions[0].serving_size  # type: ignore
        serving_size_unit = lobject.portions[0].serving_size_unit  # type: ignore
    elif hasattr(lobject, "db_food") and lobject.db_food and lobject.db_food.dbfoodportion_set.all():  # type: ignore
        cfood_portion: db_food_portion.DBFoodPortion = lobject.db_food.dbfoodportion_set.first()  # type: ignore
        if cfood_portion.serving_size is not None:
            serving_size = cfood_portion.serving_size

        if cfood_portion.serving_size_unit is not None:
            serving_size_unit = constants.ServingSizeUnit(cfood_portion.serving_size_unit)

    return serving_size, serving_size_unit


def get_items_form_data_from_preferences(
    food_preferences: list[user_preference.UserPreference],
) -> tuple[list[UUID], list[UUID], list[UUID], list[UUID]]:
    """Get food preferences form data."""
    available_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
        food_preferences, flags_set=[user_preference.FLAG_IS_AVAILABLE]
    )
    available_items: list[UUID] = [fp.food_external_id for fp in available_preferences if fp.food_external_id]

    must_have_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
        food_preferences, flags_set=[user_preference.FLAG_IS_NOT_ZEROABLE]
    )
    must_have_items: list[UUID] = [fp.food_external_id for fp in must_have_preferences if fp.food_external_id]

    dont_have_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
        food_preferences, flags_set=[user_preference.FLAG_IS_NOT_ALLOWED]
    )
    dont_have_items: list[UUID] = [fp.food_external_id for fp in dont_have_preferences if fp.food_external_id]

    dont_repeat_preferences: list[user_preference.UserPreference] = user_prefs.filter_preferences(
        food_preferences, flags_set=[user_preference.FLAG_IS_NOT_REPEATABLE]
    )
    dont_repeat_items: list[UUID] = [fp.food_external_id for fp in dont_repeat_preferences if fp.food_external_id]

    return available_items, must_have_items, dont_have_items, dont_repeat_items
