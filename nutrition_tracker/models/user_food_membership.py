"""Model and APIs for user created memberships. This table stores relationships such as meal => {ingredient|recipe}, recipe => {ingredient|recipe}"""
from __future__ import annotations

import uuid
from typing import Any, MutableMapping

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Prefetch, QuerySet

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_food_portion


class UserFoodMembership(user_base.UserBase):
    """DB Model for user food memberships."""

    external_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="external_id",
        help_text="External UUID for the object.",
    )
    parent_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="parent_type")
    parent_id = models.PositiveBigIntegerField(
        verbose_name="parent_id",
        help_text="Unique permanent identifier of the parent object - meal, recipe, mealplan.",
    )
    parent = GenericForeignKey("parent_type", "parent_id")
    child_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="child_type")
    child_id = models.PositiveBigIntegerField(
        verbose_name="child_id", help_text="Unique permanent identifier of the child object - ingredient, recipe."
    )
    child = GenericForeignKey("child_type", "child_id")
    portion = GenericRelation(
        user_food_portion.UserFoodPortion, content_type_field="content_type", object_id_field="object_id"
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_food_membership"
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_parent_child_different",
                check=~(models.Q(parent_id=models.F("child_id")) & models.Q(parent_type=models.F("child_type"))),
            )
        ]


def empty_qs() -> QuerySet[UserFoodMembership]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserFoodMembership)


def _load_queryset(luser: user_model.User) -> QuerySet[UserFoodMembership]:
    """Base QuerySet for user food memberships. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {
        "user__in": user.get_family_members(luser) or [luser]
    }
    return UserFoodMembership.objects.prefetch_related(Prefetch("portion", to_attr="portions")).filter(**params)


def load_lmembership(
    luser: user_model.User, id_: int | None = None, external_id: str | uuid.UUID | None = None
) -> UserFoodMembership | None:
    """Loads a user food membership object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id

    return db_models.load(UserFoodMembership, _load_queryset(luser), params)


def load_lmemberships(  # pylint: disable=too-many-arguments
    luser: user_model.User,
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    parent_id: int | None = None,
    parent_type_id: int | None = None,
    child_id: int | None = None,
    child_type_id: int | None = None,
) -> QuerySet[UserFoodMembership]:
    """Batch load user food membership objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []

    qs: QuerySet[UserFoodMembership] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if parent_id:
        params["parent_id"] = parent_id
    if parent_type_id:
        params["parent_type_id"] = parent_type_id
    if child_id:
        params["child_id"] = child_id
    if child_type_id:
        params["child_type_id"] = child_type_id

    return qs.filter(**params)


def create(luser: user_model.User, **kwargs: Any) -> UserFoodMembership:
    """Create and save a user food membership in the database."""
    return db_models.create(UserFoodMembership, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserFoodMembership, bool]:
    """Lookup a user food membership, creating one if necessary in the database."""
    return db_models.get_or_create(UserFoodMembership, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserFoodMembership, bool]:
    """Update a user food membership with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserFoodMembership, defaults=defaults, user=luser, **kwargs)
