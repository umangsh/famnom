"""User logic module."""
from __future__ import annotations

import uuid
from typing import Any

from allauth.utils import get_user_model
from django.db import models

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.utils import exceptions


def get_flags(flags_dict: dict[str, bool]) -> int:
    """Get flags dict as an int."""
    return db_models.get_flags(get_user_model(), flags_dict)


def empty_qs() -> models.QuerySet[user_model.User]:
    """Empty QuerySet."""
    return db_models.empty_qs(get_user_model())


def _load_queryset() -> models.QuerySet[user_model.User]:
    """Base queryset for user model DB queries.
    All queries filter on this queryset."""
    return get_user_model().objects.all()


def load_luser(
    id_: int | None = None, external_id: str | uuid.UUID | None = None, email: str | None = None
) -> user_model.User | None:
    """Loads a user object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id
    if email:
        params["email"] = email

    return db_models.load(get_user_model(), _load_queryset(), params)


def load_lusers(
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    emails: list[str] | None = None,
    family_id: str | uuid.UUID | None = None,
) -> models.QuerySet[user_model.User]:
    """Batch load user objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []
    if not emails:
        emails = []

    qs: models.QuerySet[user_model.User] = _load_queryset()

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids
    if emails:
        params["email__in"] = emails

    qs = db_models.bulk_load(qs, params)

    params = {}
    if family_id:
        params["family_id"] = family_id

    return qs.filter(**params)


def create_family(parent_luser: user_model.User, child_email: str) -> None:
    """Create a family of parent_luser and child_email.
    Add to family if already exists, create one otherwise."""
    if parent_luser.email == child_email:
        return

    child_luser: user_model.User | None = load_luser(email=child_email)
    if not child_luser:
        return

    if parent_luser.family_id:
        add_to_family(child_luser, parent_luser.family_id)
    else:
        family_id: uuid.UUID = uuid.uuid4()
        add_to_family(child_luser, family_id)
        add_to_family(parent_luser, family_id)


def add_to_family(luser: user_model.User, family_id: str | uuid.UUID | None) -> None:
    """Add user to family keyed by family_id."""
    if not family_id:
        return

    if luser.family_id and luser.family_id != family_id:
        raise exceptions.UserInAnotherFamilyException(luser)

    if luser.family_id and luser.family_id == family_id:
        return

    lusers: models.QuerySet[user_model.User] = load_lusers(family_id=family_id)
    if lusers.count() >= constants.MAX_FAMILY_SIZE:
        raise exceptions.MaxFamilySizeException

    luser.family_id = family_id
    luser.save()


def get_family_members(luser: user_model.User) -> models.QuerySet[user_model.User]:
    """Returns all family members in a user's family, if exists."""
    if not luser.family_id:
        return empty_qs()

    return load_lusers(family_id=luser.family_id)
