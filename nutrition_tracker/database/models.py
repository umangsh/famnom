"""DB base APIs.

This module provides wrappers to Django QuerySet APIs
used by all models."""
from __future__ import annotations

from functools import reduce
from typing import Any, MutableMapping, TypeVar

from django.db.models import Q, QuerySet
from django.db.models.lookups import Transform

from nutrition_tracker.models import db_base


class Initcap(Transform):
    """DB Lookup transform to capitalize first letter of each word. Only works for postgresql and Oracle, not supported for MySQL."""

    function: str = "INITCAP"
    lookup_name: str = "initcap"


TDbBase = TypeVar("TDbBase", bound=db_base.DbBase)


def empty_qs(cls: type[TDbBase]) -> QuerySet[TDbBase]:
    """Empty QuerySet."""
    return cls.objects.none()


def bulk_create(
    cls: type[TDbBase], objs: list[TDbBase], batch_size: int | None = None, ignore_conflicts: bool = False
) -> list[TDbBase]:
    """Insert the provided list of objects into the database."""
    return cls.objects.bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)


def create(cls: type[TDbBase], **kwargs: Any) -> TDbBase:
    """Create and save an object in the database."""
    return cls.objects.create(**kwargs)


def get_or_create(
    cls: type[TDbBase], defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[TDbBase, bool]:
    """Lookup an object, creating one if necessary in the database."""
    return cls.objects.get_or_create(defaults=defaults, **kwargs)


def load(cls: type[TDbBase], qs: QuerySet[TDbBase], params: dict) -> TDbBase | None:
    """Returns the object matching the given lookup parameters, None if the object does not exist."""
    if not params:
        return None

    try:
        return qs.get(**params)
    except cls.DoesNotExist:
        return None


def bulk_load(qs: QuerySet[TDbBase], params: dict) -> QuerySet[TDbBase]:
    """Filters the input queryset matching the given params, returns the unfiltered queryset if params are None."""
    if params:
        fields = [Q(**{key: params[key]}) for key in params]
        filters = reduce(lambda x, y: x | y, fields)
        qs = qs.filter(filters)

    return qs


def bulk_update(cls: type[TDbBase], objs: list[TDbBase], fields: list[str], batch_size: int | None = None) -> None:
    """Update the given fields on the provided model instances."""
    return cls.objects.bulk_update(objs, fields, batch_size=batch_size)


def update(cls: type[TDbBase], **kwargs: Any) -> int:
    """Updates the database model for the specified fields, and returns the number of rows matched."""
    return cls.objects.update(**kwargs)


def update_or_create(
    cls: type[TDbBase], defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[TDbBase, bool]:
    """Update an object with the given kwargs, creating a new one if necessary."""
    return cls.objects.update_or_create(defaults=defaults, **kwargs)


def get_flags(cls: type[TDbBase], flags_dict: dict[str, bool]) -> int:
    """Convert a map of flag values to an int of flag bits."""
    flags: int = 0
    for name in flags_dict:
        value: bool = flags_dict[name]
        if value:
            flags |= getattr(cls.flags, name)  # type: ignore

    return flags
