"""Model and APIs for user created meals."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Any, MutableMapping

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Prefetch, QuerySet
from django.utils import timezone
from django.utils.functional import cached_property

import users.models as user_model
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_food_membership
from nutrition_tracker.utils import text


class UserMeal(user_base.UserBase):
    """DB Model for user meals."""

    external_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="external_id",
        help_text="External UUID for the object.",
    )
    meal_date = models.DateField(
        null=True, blank=True, default=date.today, verbose_name="meal_date", help_text="Date when the meal was logged."
    )
    meal_type = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="meal type", help_text="Type of meal."
    )
    membership = GenericRelation(
        user_food_membership.UserFoodMembership, content_type_field="parent_type", object_id_field="parent_id"
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_meal"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_meal_type_and_date_per_user",
                fields=["user_id", "meal_type", "meal_date"],
            ),
        ]
        indexes = [
            models.Index(name="user_meal_user_mealdate_idx", fields=["user_id", "meal_date"]),
        ]

    def display_name(self, with_date: bool = True) -> str | None:
        """Formatted meal name for display."""
        if with_date:
            return f"{self.meal_type}: {self.display_date}"

        return self.meal_type

    @cached_property
    def display_date(self) -> str:
        """Formatted meal date for display."""
        return text.format_date(self.meal_date)


def empty_qs() -> QuerySet[UserMeal]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserMeal)


def _load_queryset(luser: user_model.User) -> QuerySet[UserMeal]:
    """Base QuerySet for user meals. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    return UserMeal.objects.prefetch_related(
        Prefetch(
            "membership",
            to_attr="members",
            queryset=user_food_membership.UserFoodMembership.objects.prefetch_related(
                "child", Prefetch("portion", to_attr="portions")
            ),
        )
    ).filter(user=luser)


def load_lmeal(
    luser: user_model.User, id_: int | None = None, external_id: str | uuid.UUID | None = None
) -> UserMeal | None:
    """Loads a user meal object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id

    return db_models.load(UserMeal, _load_queryset(luser), params)


def load_lmeals(  # pylint: disable=too-many-arguments
    luser: user_model.User,
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    order_by: str | None = None,
    meal_date: date | None = None,
    num_days: int | None = None,
    max_rows: int | None = None,
) -> QuerySet[UserMeal]:
    """Batch load user meal objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []

    qs: QuerySet[UserMeal] = _load_queryset(luser)

    if meal_date:
        if num_days:
            start_date = meal_date - timezone.timedelta(days=num_days)
            qs = qs.filter(meal_date__range=[start_date, meal_date])
        else:
            qs = qs.filter(meal_date=meal_date)

    if order_by:
        qs = qs.order_by(order_by)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids

    qs = db_models.bulk_load(qs, params)
    if max_rows:
        qs = qs[:max_rows]

    return qs


def load_latest_lmeal(luser: user_model.User, meal_date: date) -> UserMeal | None:
    """Loads the latest meal object for a user."""
    qs: QuerySet[UserMeal] = load_lmeals(luser, meal_date=meal_date)

    if not qs:
        return None

    return qs.latest("updated_timestamp")


def create(luser: user_model.User, **kwargs: Any) -> UserMeal:
    """Create and save a user meal in the database."""
    return db_models.create(UserMeal, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserMeal, bool]:
    """Lookup a user meal, creating one if necessary in the database."""
    return db_models.update_or_create(UserMeal, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserMeal, bool]:
    """Update a user meal with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserMeal, defaults=defaults, user=luser, **kwargs)
