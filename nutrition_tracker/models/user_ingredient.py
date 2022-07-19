"""Model and APIs for user created foods/ingredients."""
from __future__ import annotations

import uuid
from typing import Any, MutableMapping, Sequence

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Case, OuterRef, Prefetch, Q, QuerySet, Subquery, When
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_food, user_base, user_food_membership, user_food_portion


class UserIngredient(user_base.UserBase):
    """DB Model for user foods/ingredients."""

    external_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="external_id",
        help_text="External UUID for the object.",
    )
    name = models.TextField(null=True, blank=True, verbose_name="name", help_text="Name of the object.")
    db_food = models.ForeignKey(
        db_food.DBFood,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="db_food",
        help_text="DB Food for this ingredient",
    )
    portion = GenericRelation(
        user_food_portion.UserFoodPortion, content_type_field="content_type", object_id_field="object_id"
    )
    membership = GenericRelation(
        user_food_membership.UserFoodMembership, content_type_field="child_type", object_id_field="child_id"
    )
    category_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="food_category_id",
        help_text="Id of the food category the food belongs to.",
    )

    class Meta(user_base.UserBase.Meta):
        db_table = "ut_user_ingredient"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_db_food_per_food_per_user", fields=["user_id", "db_food_id"]
            ),
        ]

    @cached_property
    def display_name(self) -> str | None:
        """Formatted ingredient name for display."""
        if hasattr(self, "coalesced_name"):
            return self.coalesced_name  # type: ignore

        if self.name:
            return self.name

        if self.db_food:
            return self.db_food.display_name

        return ""

    def display_brand_field(self, fieldname: str) -> str | None:
        """Formatted brand field for display."""
        if hasattr(self, "branded_foods") and self.branded_foods:  # type: ignore
            fieldvalue = getattr(self.branded_foods[0], fieldname, "")  # type: ignore
            if fieldvalue:
                return fieldvalue

        if self.db_food:
            return self.db_food.display_brand_field(fieldname)

        return ""

    @cached_property
    def display_brand_details(self) -> str:
        """Formatted brand details for display."""
        brand_fields = constants.BRAND_FIELDS[:-1]
        fieldvalues = [self.display_brand_field(f) for f in brand_fields]
        return ", ".join([value for value in fieldvalues if value])


def empty_qs() -> QuerySet[UserIngredient]:
    """Empty QuerySet."""
    return db_models.empty_qs(UserIngredient)


def _load_queryset(luser: user_model.User) -> QuerySet[UserIngredient]:
    """Base QuerySet for user foods/ingredients. All other APIs filter on this queryset."""
    if not luser.is_authenticated:
        return empty_qs()

    params: dict[str, QuerySet[user_model.User] | list[user_model.User]] = {
        "user__in": user.get_family_members(luser) or [luser]
    }
    return (
        UserIngredient.objects.prefetch_related(
            Prefetch(
                "db_food",
                queryset=db_food.DBFood.objects.select_related("dbbrandedfood").prefetch_related("dbfoodportion_set"),
            ),
            Prefetch("userbrandedfood_set", to_attr="branded_foods"),
            Prefetch("portion", to_attr="portions"),
        )
        .filter(**params)
        .annotate(coalesced_name=Coalesce("name", "db_food__description"))
        .annotate(coalesced_gtin_upc=Coalesce("userbrandedfood__gtin_upc", "db_food__dbbrandedfood__gtin_upc"))
        .annotate(coalesced_brand_name=Coalesce("userbrandedfood__brand_name", "db_food__dbbrandedfood__brand_name"))
        .annotate(
            coalesced_subbrand_name=Coalesce("userbrandedfood__subbrand_name", "db_food__dbbrandedfood__subbrand_name")
        )
        .annotate(
            coalesced_brand_owner=Coalesce("userbrandedfood__brand_owner", "db_food__dbbrandedfood__brand_owner")
        )
    )


def _filter_duplicate_db_foods(luser: user_model.User, qs: QuerySet[UserIngredient]) -> QuerySet[UserIngredient]:
    """Filter duplicate foods in queryset."""
    if not luser.is_authenticated:
        return qs

    if not user.get_family_members(luser):
        return qs

    qs1 = (
        UserIngredient.objects.select_related("user")
        .filter(db_food=OuterRef("db_food"))
        .annotate(user_match=Case(When(user=luser, then=0), default=1))
        .order_by("user_match", "user__family_added_timestamp")
    )

    return qs.filter(Q(db_food__isnull=True) | Q(id=Subquery(qs1.values("id")[:1])))


def load_lfood(
    luser: user_model.User,
    id_: int | None = None,
    external_id: str | uuid.UUID | None = None,
    db_food_id: int | None = None,
) -> UserIngredient | None:
    """Loads a user ingredient object."""
    qs: QuerySet[UserIngredient] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id
    if db_food_id:
        params["db_food_id"] = db_food_id

    # De-dupe by db_food unless loading lfoods by id or external_id
    # The default behavior filters duplicate foods on browse.
    # Lookups by ID (my_food pages) should always render the item
    # even if it's a duplicate food.
    if not id_ and not external_id:
        qs = _filter_duplicate_db_foods(luser, qs)

    return db_models.load(UserIngredient, qs, params)


def load_lfoods(
    luser: user_model.User,
    ids: list[int] | None = None,
    external_ids: Sequence[str | uuid.UUID] | None = None,
    db_food_ids: list[int] | None = None,
) -> QuerySet[UserIngredient]:
    """Batch load user ingredient objects."""
    if ids is None:
        ids = []
    if external_ids is None:
        external_ids = []
    if db_food_ids is None:
        db_food_ids = []

    qs: QuerySet[UserIngredient] = _load_queryset(luser)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids
    if db_food_ids:
        params["db_food_id__in"] = db_food_ids

    if not ids and not external_ids:
        qs = _filter_duplicate_db_foods(luser, qs)

    return db_models.bulk_load(qs, params)


def load_lfoods_for_browse(
    luser: user_model.User, external_ids: Sequence[str | uuid.UUID] | None = None, query: str | None = None
) -> QuerySet[UserIngredient]:
    """Batch load user ingredient objects for browse contexts - supports filter by query."""
    if external_ids is None:
        external_ids = []

    qs: QuerySet[UserIngredient] = load_lfoods(luser, external_ids=external_ids)
    if query:
        qs = qs.filter(
            Q(coalesced_name__unaccent__icontains=query)
            | Q(coalesced_brand_name__unaccent__icontains=query)
            | Q(coalesced_subbrand_name__unaccent__icontains=query)
            | Q(coalesced_brand_owner__unaccent__icontains=query)
            | Q(coalesced_gtin_upc=query)
        )

    return qs.order_by("coalesced_name")


def create(luser: user_model.User, **kwargs: Any) -> UserIngredient:
    """Create and save a user ingredient in the database."""
    return db_models.create(UserIngredient, user=luser, **kwargs)


def get_or_create(luser: user_model.User, **kwargs: Any) -> tuple[UserIngredient, bool]:
    """Lookup a user ingredient, creating one if necessary in the database."""
    return db_models.update_or_create(UserIngredient, user=luser, **kwargs)


def update_or_create(
    luser: user_model.User, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[UserIngredient, bool]:
    """Update a user ingredient with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(UserIngredient, defaults=defaults, user=luser, **kwargs)
