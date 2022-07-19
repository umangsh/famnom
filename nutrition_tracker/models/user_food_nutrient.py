"""Model and APIs for user created food nutrients."""
from __future__ import annotations

from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_ingredient


class UserFoodNutrient(user_base.UserBase):
    """DB Model for user food nutrients."""

    ingredient = models.ForeignKey(
        user_ingredient.UserIngredient,
        on_delete=models.CASCADE,
        verbose_name="ingredient",
        help_text="Parent food for the nutrition information.",
    )
    nutrient_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="nutrient_id",
        help_text="ID of the nutrient to which the food nutrient pertains.",
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=("Amount of the nutrient per 100g of food. " "Specified in unit defined in the nutrient table."),
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_food_nutrient"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_nutrient_per_food_per_user",
                fields=["user_id", "ingredient_id", "nutrient_id"],
            ),
        ]


def empty_qs() -> QuerySet[UserFoodNutrient]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserFoodNutrient)


def _load_queryset(luser: user_model.User) -> QuerySet[UserFoodNutrient]:
    """Base QuerySet for user food nutrients. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {
        "user__in": user.get_family_members(luser) or [luser]
    }
    return UserFoodNutrient.objects.select_related("ingredient").filter(**params)


def load_nutrients(
    luser: user_model.User,
    ids: list[int] | None = None,
    ingredients: list[user_ingredient.UserIngredient] | None = None,
    nutrient_ids: list[int] | None = None,
) -> QuerySet[UserFoodNutrient]:
    """Batch load user food nutrient objects."""
    if not ids:
        ids = []
    if not ingredients:
        ingredients = []
    if not nutrient_ids:
        nutrient_ids = []

    qs: QuerySet[UserFoodNutrient] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if ingredients:
        params["ingredient__in"] = ingredients

    qs = db_models.bulk_load(qs, params)

    params = {}
    if nutrient_ids:
        params["nutrient_id__in"] = nutrient_ids

    return qs.filter(**params)


def create(luser: user_model.User, **kwargs: Any) -> UserFoodNutrient:
    """Create and save a user food nutrient in the database."""
    return db_models.create(UserFoodNutrient, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserFoodNutrient, bool]:
    """Update a user food nutrient with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserFoodNutrient, defaults=defaults, user=luser, **kwargs)
