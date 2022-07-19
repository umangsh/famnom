"""User preferences logic module."""
from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_preference, user_preference_threshold


def load_nutrition_preferences(user: user_model.User) -> QuerySet[user_preference.UserPreference]:
    """Load nutrition preferences for a user."""
    qs: QuerySet[user_preference.UserPreference] = user_preference.load_luser_preferences(user)
    return qs.exclude(food_nutrient_id__isnull=True)


def load_food_preferences(user: user_model.User) -> QuerySet[user_preference.UserPreference]:
    """Load food preferences for a user."""
    qs: QuerySet[user_preference.UserPreference] = user_preference.load_luser_preferences(user)
    return qs.exclude(food_external_id__isnull=True)


def filter_preferences_by_id(
    luser_preferences: list[user_preference.UserPreference],
    food_external_id: UUID | None = None,
    food_category_id: int | None = None,
    food_nutrient_id: int | None = None,
) -> user_preference.UserPreference | None:
    """Filter list of preferences by food/category/nutrient ID."""
    if not luser_preferences:
        return None

    if food_external_id is not None:
        return next((fp for fp in luser_preferences if fp.food_external_id == food_external_id), None)

    if food_category_id is not None:
        return next((fp for fp in luser_preferences if fp.food_category_id == food_category_id), None)

    if food_nutrient_id is not None:
        return next((fp for fp in luser_preferences if fp.food_nutrient_id == food_nutrient_id), None)

    return None


def filter_preferences(
    luser_preferences: list[user_preference.UserPreference],
    flags_set: list[str] | None = None,
    flags_unset: list[str] | None = None,
    flags_set_any: list[str] | None = None,
) -> list[user_preference.UserPreference]:
    """
    Filter user preferences based on flags.
    flags_set/flags_unset: AND operators.
    flags_set_any: OR operators.
    """
    if not flags_set:
        flags_set = []
    if not flags_unset:
        flags_unset = []
    if not flags_set_any:
        flags_set_any = []

    if flags_set:
        luser_preferences = [fp for fp in luser_preferences if all(fp.get_flag(flag) for flag in flags_set)]

    if flags_unset:
        luser_preferences = [fp for fp in luser_preferences if all(not fp.get_flag(flag) for flag in flags_unset)]

    if flags_set_any:
        luser_preferences = [fp for fp in luser_preferences if any(fp.get_flag(flag) for flag in flags_set_any)]

    return luser_preferences


def filter_food_preferences(
    luser_preferences: list[user_preference.UserPreference],
) -> list[user_preference.UserPreference]:
    """Filter user preferences to food preferences."""
    return [
        luser_preference for luser_preference in luser_preferences if luser_preference.food_external_id is not None
    ]


def filter_category_preferences(
    luser_preferences: list[user_preference.UserPreference],
) -> list[user_preference.UserPreference]:
    """Filter user preferences to category preferences."""
    return [
        luser_preference for luser_preference in luser_preferences if luser_preference.food_category_id is not None
    ]


def filter_nutrient_preferences(
    luser_preferences: list[user_preference.UserPreference],
) -> list[user_preference.UserPreference]:
    """Filter user preferences to nutrient preferences."""
    return [
        luser_preference for luser_preference in luser_preferences if luser_preference.food_nutrient_id is not None
    ]


def filter_preference_thresholds(
    luser_preference_thresholds: list[user_preference_threshold.UserPreferenceThreshold],
    dimension: constants.Dimension = constants.Dimension.QUANTITY,
    days: int = 1,
    expansion_set: constants.ExpansionSet = constants.ExpansionSet.SELF,
) -> user_preference_threshold.UserPreferenceThreshold | None:
    """Filter user preference thresholds."""
    return next(
        (
            threshold
            for threshold in luser_preference_thresholds
            if threshold.dimension == dimension
            and threshold.num_days == days
            and threshold.expansion_set == expansion_set
        ),
        None,
    )


def get_threshold_value(
    luser_preference: user_preference.UserPreference,
    dimension: constants.Dimension = constants.Dimension.QUANTITY,
    days: int = 1,
    expansion_set: constants.ExpansionSet = constants.ExpansionSet.SELF,
) -> float | None:
    """Get user preference threshold value."""
    if not luser_preference:
        return None

    threshold: user_preference_threshold.UserPreferenceThreshold | None = filter_preference_thresholds(
        list(luser_preference.userpreferencethreshold_set.all()),
        dimension=dimension,
        days=days,
        expansion_set=expansion_set,
    )

    if threshold:
        return threshold.exact_value or threshold.min_value or threshold.max_value

    return None
