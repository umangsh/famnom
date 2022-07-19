"""Planner utility methods."""
from __future__ import annotations

import uuid


def get_quantity_variable(base_id: int | str | uuid.UUID, day: int = 1) -> str:
    """Get quantity variable for an item with base_id.
    Quantity variable represent the quantity used for a given item during meal planning."""
    to_return = f"{base_id}:q"
    if day is not None:
        to_return = f"{to_return}{day}"

    return to_return


def is_quantity_variable(variable_name: str) -> bool:
    """Is quantity variable."""
    return ":q" in variable_name


def get_presence_variable(base_id: int | str | uuid.UUID, day: int = 1) -> str:
    """Get presence variable for an item with base_id.
    Presence variable represent whether the item is present in the proposed mealplan."""
    to_return = f"{base_id}:p"
    if day is not None:
        to_return = f"{to_return}{day}"

    return to_return


def is_presence_variable(variable_name: str) -> bool:
    """Is presence variable."""
    return ":p" in variable_name


def get_sum_variable(base_id: int | str | uuid.UUID, day: int = 1) -> str:
    """Get sum variable for an item with base_id.
    Sum variable represent the sum of quantities of member items (for categories, for e.g.)."""
    to_return = f"{base_id}:s"
    if day is not None:
        to_return = f"{to_return}{day}"

    return to_return


def is_sum_variable(variable_name: str) -> bool:
    """Is sum variable."""
    return ":s" in variable_name


def get_constraint_variable(base_id: int | str | uuid.UUID, day: int = 1) -> str:
    """Get constraint variable for an item with base_id.
    Constraint variable represent whether the constraint item_id is true in the proposed mealplan."""
    to_return = f"{base_id}-{uuid.uuid4()}:c"
    if day is not None:
        to_return = f"{to_return}{day}"

    return to_return


def is_constraint_variable(variable_name: str) -> bool:
    """Is constraint variable."""
    return ":c" in variable_name
