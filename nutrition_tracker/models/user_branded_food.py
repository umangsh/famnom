"""Model and APIs for user branded food metadata."""
from __future__ import annotations

from typing import Any, MutableMapping

from django.db import models
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_ingredient


class UserBrandedFood(user_base.UserBase):
    """DB Model for user branded food metadata."""

    ingredient = models.ForeignKey(
        user_ingredient.UserIngredient,
        on_delete=models.CASCADE,
        verbose_name="ingredient",
        help_text="Parent food for the brand information.",
    )
    brand_owner = models.TextField(
        null=True, blank=True, verbose_name="brand_owner", help_text="Brand owner for the food."
    )
    brand_name = models.TextField(
        null=True, blank=True, verbose_name="brand_name", help_text="Brand name for the food."
    )
    subbrand_name = models.TextField(
        null=True, blank=True, verbose_name="subbrand_name", help_text="Sub-brand name for the food."
    )
    gtin_upc = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="gtin_upc",
        help_text="GTIN or UPC code identifying the food.",
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_branded_food"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_row_per_food_per_user", fields=["user_id", "ingredient_id"]
            ),
        ]
        indexes = [
            models.Index(name="user_branded_food_gtinupc_idx", fields=["user_id", "gtin_upc"]),
        ]


def empty_qs() -> QuerySet[UserBrandedFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserBrandedFood)


def _load_queryset(luser: user_model.User) -> QuerySet[UserBrandedFood]:
    """Base QuerySet for user branded food. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {}
    params["user__in"] = user.get_family_members(luser) or [luser]
    return UserBrandedFood.objects.select_related("ingredient").filter(**params)


def load_lbranded_food(
    luser: user_model.User,
    id_: int | None = None,
    ingredient_id: int | None = None,
    gtin_upc: str | None = None,
) -> UserBrandedFood | None:
    """Loads a user branded food object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if ingredient_id:
        params["ingredient_id"] = ingredient_id
    if gtin_upc:
        params["gtin_upc"] = gtin_upc

    return db_models.load(UserBrandedFood, _load_queryset(luser), params)


def load_lbranded_foods(
    luser: user_model.User,
    ids: list[int] | None = None,
    ingredient_ids: list[int] | None = None,
    gtin_upcs: list[str] | None = None,
) -> QuerySet[UserBrandedFood]:
    """Batch load user branded food objects."""
    if not ids:
        ids = []
    if not ingredient_ids:
        ingredient_ids = []
    if not gtin_upcs:
        gtin_upcs = []

    qs: QuerySet[UserBrandedFood] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if ingredient_ids:
        params["ingredient_id__in"] = ingredient_ids
    if gtin_upcs:
        params["gtin_upc__in"] = gtin_upcs

    return db_models.bulk_load(qs, params)


def create(luser: user_model.User, **kwargs: Any) -> UserBrandedFood:
    """Create and save a user branded food row in the database."""
    return db_models.create(UserBrandedFood, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserBrandedFood, bool]:
    """Update a user branded food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserBrandedFood, defaults=defaults, user=luser, **kwargs)
