"""Model and APIs for user created food portions."""
from __future__ import annotations

import uuid
from typing import Any, MutableMapping

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base


class UserFoodPortion(user_base.UserBase):  # pylint: disable=too-many-instance-attributes
    """DB Model for user food portions."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField(
        verbose_name="object_id", help_text="Unique permanent identifier of the referenced object."
    )
    content_object = GenericForeignKey("content_type", "object_id")
    external_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    servings_per_container = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="servings_per_container",
        help_text="The number of servings per container.",
    )
    serving_size = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="serving_size",
        help_text="The amount of the serving size when expressed as gram or ml.",
    )
    serving_size_unit = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        verbose_name="serving_size_unit",
        help_text="The unit used to express the serving size (gram or ml).",
    )
    quantity = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="quantity",
        help_text=("The quantity of portions used as specified by the user."),
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=(
            "The number of measure units that comprise the measure " "(e.g. if measure is 3 tsp, the amount is 3)."
        ),
    )
    measure_unit_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="measure_unit_id",
        help_text=("The unit used for the measure (e.g. if measure is 3 tsp, " "the unit is tsp)."),
    )
    portion_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="portion_description",
        help_text=(
            "Foundation foods: Comments that provide more specificity "
            "on the measure. For example, for a pizza measure the "
            "dissemination text might be 1 slice is 1/8th of a 14 "
            "inch pizza. "
            "Survey (FNDDS) foods: The household description of the portion."
        ),
    )
    modifier = models.TextField(
        null=True,
        blank=True,
        verbose_name="modifier",
        help_text=(
            "Foundation foods: Qualifier of the measure (e.g. related "
            "to food shape or form) (e.g. melted, crushed, diced). "
            "Survey (FNDDS) foods: The portion code. "
            "SR legacy foods: description of measures, including the "
            'unit of measure and the measure modifier (e.g. waffle round (4" dia)).'
        ),
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_food_portion"
        ordering = ["id"]


def empty_qs() -> QuerySet[UserFoodPortion]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserFoodPortion)


def _load_queryset(luser: user_model.User) -> QuerySet[UserFoodPortion]:
    """Base QuerySet for user food portions. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {
        "user__in": user.get_family_members(luser) or [luser]
    }
    return UserFoodPortion.objects.filter(**params)


def load_lfood_portions(luser: user_model.User, ids: list[int] | None = None) -> QuerySet[UserFoodPortion]:
    """Batch load user food portion objects."""
    if not ids:
        ids = []

    qs: QuerySet[UserFoodPortion] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids

    return db_models.bulk_load(qs, params)


def create(luser: user_model.User, **kwargs: Any) -> UserFoodPortion:
    """Create and save a user food portion in the database."""
    return db_models.create(UserFoodPortion, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserFoodPortion, bool]:
    """Update a user food portion with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserFoodPortion, defaults=defaults, user=luser, **kwargs)
