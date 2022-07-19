"""Model and APIs for user preference thresholds."""
from __future__ import annotations

from typing import Any

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_preference


class UserPreferenceThreshold(user_base.UserBase):
    """DB Model for user preference thresholds."""

    user_preference = models.ForeignKey(
        user_preference.UserPreference,
        on_delete=models.CASCADE,
        verbose_name="user preference",
        help_text="User Preference parent object.",
    )
    dimension = models.PositiveSmallIntegerField(
        default=constants.Dimension.QUANTITY,
        choices=constants.Dimension.choices,
        verbose_name="dimension",
        help_text="Preference threshold applied to quantity or count dimension.",
    )
    num_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=1,
        verbose_name="num_days",
        help_text="Number of days the preference threshold is applicable to.",
    )
    min_value = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="min_value",
        help_text="The minimum value for the preference threshold.",
    )
    max_value = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="max_value",
        help_text="The maximum value for the preference threshold.",
    )
    exact_value = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="exact_value",
        help_text="The exact value for the preference threshold.",
    )
    expansion_set = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=constants.ExpansionSet.SELF,
        choices=constants.ExpansionSet.choices,
        verbose_name="expansion_set",
        help_text="Apply the preference threshold to self or group members.",
    )

    class Meta(user_base.UserBase.Meta):
        """Meta class for user preference thresholds."""

        db_table = "ut_user_preference_threshold"


def empty_qs() -> QuerySet[UserPreferenceThreshold]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserPreferenceThreshold)


def create(luser: user_model.User, **kwargs: Any) -> UserPreferenceThreshold:
    """Create and save a user preference threshold in the database."""
    return db_models.create(UserPreferenceThreshold, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserPreferenceThreshold, bool]:
    """Lookup a user preference threshold, creating one if necessary in the database."""
    return db_models.get_or_create(UserPreferenceThreshold, user=luser, **kwargs)
