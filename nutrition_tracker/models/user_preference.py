"""Model and APIs for user preferences."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from bitfield import BitField
from django.db import models
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base

FLAG_IS_NOT_ALLOWED = "is_not_allowed"
FLAG_IS_AVAILABLE = "is_available"
FLAG_IS_NOT_REPEATABLE = "is_not_repeatable"
FLAG_IS_NOT_ZEROABLE = "is_not_zeroable"


class UserPreference(user_base.UserBase):
    """DB Model for user preferences."""

    food_external_id = models.UUIDField(
        null=True, blank=True, verbose_name="food_external_id", help_text="External food ID for the food."
    )
    food_category_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="food_category_id",
        help_text="Id of the food category the food belongs to.",
    )
    food_nutrient_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="food_nutrient_id",
        help_text="ID of the nutrient to which the food nutrient pertains.",
    )
    flags = BitField(
        flags=(
            FLAG_IS_NOT_ALLOWED,
            FLAG_IS_AVAILABLE,
            FLAG_IS_NOT_REPEATABLE,
            FLAG_IS_NOT_ZEROABLE,
        )
    )

    class Meta(user_base.UserBase.Meta):
        """Meta class for user preferences."""

        db_table = "ut_user_preference"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_food_preference_per_user", fields=["user_id", "food_external_id"]
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_category_preference_per_user", fields=["user_id", "food_category_id"]
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_nutrient_preference_per_user", fields=["user_id", "food_nutrient_id"]
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_one_of_food_category_nutrient_set",
                check=(
                    models.Q(
                        food_external_id__isnull=False,
                        food_category_id__isnull=True,
                        food_nutrient_id__isnull=True,
                    )
                    | models.Q(
                        food_external_id__isnull=True,
                        food_category_id__isnull=False,
                        food_nutrient_id__isnull=True,
                    )
                    | models.Q(
                        food_external_id__isnull=True,
                        food_category_id__isnull=True,
                        food_nutrient_id__isnull=False,
                    )
                ),
            ),
        ]

    def get_flag(self, name: str) -> bool:
        """Get flag value."""
        return getattr(self.flags, name)

    def add_flag(self, name: str) -> None:
        """Add flag."""
        self.flags |= getattr(self.__class__.flags, name)

    def remove_flag(self, name: str) -> None:
        """Remove flag."""
        self.flags &= ~getattr(self.__class__.flags, name)

    def update_flag(self, name: str, value: bool) -> None:
        """Update flag."""
        if value:
            self.add_flag(name)
        else:
            self.remove_flag(name)

    def is_not_allowed(self) -> bool:
        """Return FLAG_IS_NOT_ALLOWED value."""
        return self.flags.is_not_allowed.is_set

    def is_available(self) -> bool:
        """Return FLAG_IS_AVAILABLE value."""
        return self.flags.is_available.is_set

    def is_not_repeatable(self) -> bool:
        """Return FLAG_IS_NOT_REPEATABLE value."""
        return self.flags.is_not_repeatable.is_set

    def is_not_zeroable(self) -> bool:
        """Return FLAG_IS_NOT_ZEROABLE value."""
        return self.flags.is_not_zeroable.is_set


def get_flag_names() -> list[str]:
    """Returns a list of flag names."""
    return [FLAG_IS_NOT_ALLOWED, FLAG_IS_AVAILABLE, FLAG_IS_NOT_REPEATABLE, FLAG_IS_NOT_ZEROABLE]


def empty_qs() -> QuerySet[UserPreference]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserPreference)


def _load_queryset(luser: user_model.User) -> QuerySet[UserPreference]:
    """Base QuerySet for user preferences. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    return UserPreference.objects.prefetch_related("userpreferencethreshold_set").filter(user=luser)


def load_luser_preference(
    luser: user_model.User,
    id_: int | None = None,
    food_external_id: str | UUID | None = None,
    food_category_id: int | None = None,
    food_nutrient_id: int | None = None,
) -> UserPreference | None:
    """Loads a user preference object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if food_external_id:
        params["food_external_id"] = food_external_id
    if food_category_id:
        params["food_category_id"] = food_category_id
    if food_nutrient_id:
        params["food_nutrient_id"] = food_nutrient_id

    return db_models.load(UserPreference, _load_queryset(luser), params)


def load_luser_preferences(
    luser: user_model.User,
    ids: list[int] | None = None,
    food_external_ids: list[str | UUID] | None = None,
    food_category_ids: list[int] | None = None,
    food_nutrient_ids: list[int] | None = None,
) -> QuerySet[UserPreference]:
    """Batch load user preference objects."""
    if not ids:
        ids = []
    if not food_external_ids:
        food_external_ids = []
    if not food_category_ids:
        food_category_ids = []
    if not food_nutrient_ids:
        food_nutrient_ids = []

    qs: QuerySet[UserPreference] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if food_external_ids:
        params["food_external_id__in"] = food_external_ids
    if food_category_ids:
        params["food_category_id__in"] = food_category_ids
    if food_nutrient_ids:
        params["food_nutrient_id__in"] = food_nutrient_ids

    return db_models.bulk_load(qs, params)


def bulk_create(
    objs: list[UserPreference], batch_size: int | None = None, ignore_conflicts: bool = False
) -> list[UserPreference]:
    """Insert the provided list of user preference objects into the database."""
    return db_models.bulk_create(UserPreference, objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)


def bulk_update(objs: list[UserPreference], fields: list[str], batch_size: int | None = None) -> None:
    """Update the given fields on the provided model instances."""
    return db_models.bulk_update(UserPreference, objs, fields, batch_size=batch_size)


def create(luser: user_model.User, **kwargs: Any) -> UserPreference:
    """Create and save a user preference in the database."""
    return db_models.create(UserPreference, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserPreference, bool]:
    """Lookup a user preference, creating one if necessary in the database."""
    return db_models.get_or_create(UserPreference, user=luser, **kwargs)


def get_flags(flags_dict: dict[str, bool]) -> int:
    """Convert a map of flag values to an int of flag bits."""
    return db_models.get_flags(UserPreference, flags_dict)
