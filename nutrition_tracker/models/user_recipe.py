"""Model and APIs for user created recipes."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Any, MutableMapping, Sequence

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Prefetch, QuerySet
from django.utils.functional import cached_property

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import user_base, user_food_membership, user_food_portion
from nutrition_tracker.utils import text


class UserRecipe(user_base.UserBase):
    """DB Model for user recipes."""

    external_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="external_id",
        help_text="External UUID for the object.",
    )
    name = models.TextField(null=True, blank=True, verbose_name="name", help_text="Name of the object.")
    recipe_date = models.DateField(
        default=date.today,
        blank=True,
        null=True,
        verbose_name="recipe_date",
        help_text="Date when the recipe was available.",
    )
    portion = GenericRelation(
        user_food_portion.UserFoodPortion, content_type_field="content_type", object_id_field="object_id"
    )
    from_membership = GenericRelation(
        user_food_membership.UserFoodMembership, content_type_field="parent_type", object_id_field="parent_id"
    )
    to_membership = GenericRelation(
        user_food_membership.UserFoodMembership, content_type_field="child_type", object_id_field="child_id"
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_recipe"

    def display_name(self, with_date: bool = True) -> str | None:
        """Formatted recipe name for display."""
        if with_date:
            return f"{self.name}: {self.display_date}"

        return self.name

    @cached_property
    def display_date(self) -> str:
        """Formatted recipe date for display."""
        return text.format_date(self.recipe_date)


def empty_qs() -> QuerySet[UserRecipe]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserRecipe)


def _load_queryset(luser: user_model.User) -> QuerySet[UserRecipe]:
    """Base QuerySet for user recipes. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {
        "user__in": user.get_family_members(luser) or [luser]
    }
    return UserRecipe.objects.prefetch_related(
        Prefetch("portion", to_attr="portions"),
        Prefetch(
            "from_membership",
            to_attr="members",
            queryset=user_food_membership.UserFoodMembership.objects.prefetch_related(
                "child", Prefetch("portion", to_attr="portions")
            ),
        ),
    ).filter(**params)


def load_lrecipe(
    luser: user_model.User, id_: int | None = None, external_id: str | uuid.UUID | None = None
) -> UserRecipe | None:
    """Loads a user recipe object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id

    return db_models.load(UserRecipe, _load_queryset(luser), params)


def load_lrecipes(
    luser: user_model.User,
    ids: list[int] | None = None,
    external_ids: Sequence[str | uuid.UUID] | None = None,
    order_by: str | None = None,
) -> QuerySet[UserRecipe]:
    """Batch load user recipe objects."""
    if ids is None:
        ids = []
    if external_ids is None:
        external_ids = []

    qs: QuerySet[UserRecipe] = _load_queryset(luser)

    if order_by:
        qs = qs.order_by(order_by)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids

    return db_models.bulk_load(qs, params)


def load_lrecipes_for_browse(
    luser: user_model.User,
    external_ids: Sequence[str | uuid.UUID] | None = None,
    query: str | None = None,
    order_by: str | None = None,
) -> QuerySet[UserRecipe]:
    """Batch load user recipe objects for browse contexts - supports filter by query."""
    if external_ids is None:
        external_ids = []

    qs: QuerySet[UserRecipe] = load_lrecipes(luser, external_ids=external_ids, order_by=order_by)

    if query:
        qs = qs.filter(name__unaccent__icontains=query)

    return qs


def create(luser: user_model.User, **kwargs: Any) -> UserRecipe:
    """Create and save a user recipe in the database."""
    return db_models.create(UserRecipe, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserRecipe, bool]:
    """Lookup a user recipe, creating one if necessary in the database."""
    return db_models.update_or_create(UserRecipe, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserRecipe, bool]:
    """Update a user recipe with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserRecipe, defaults=defaults, user=luser, **kwargs)
