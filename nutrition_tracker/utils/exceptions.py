"""Custom exceptions."""
from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

from nutrition_tracker.constants import constants


class MyBaseException(Exception):
    """Base class for other exceptions."""


class UserInAnotherFamilyException(MyBaseException):
    """Raised when a user already exists in another family."""

    # luser is type users.User, but cannot be imported from this module due to circular imports.
    def __init__(self, luser: Any) -> None:
        super().__init__()
        self.message = _(f"{luser.email} can not be added to your family.")


class MaxFamilySizeException(MyBaseException):
    """Raised when trying to add a User to a family with maximum members."""

    def __init__(self) -> None:
        super().__init__()
        self.message = _(f"Can not add more than {constants.MAX_FAMILY_SIZE} members to a family.")
