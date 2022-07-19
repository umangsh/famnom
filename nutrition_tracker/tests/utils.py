"""Util functions used by python tests."""
from __future__ import annotations

import logging
import os
from typing import Any, Callable


def prevent_request_warnings(original_function: Callable) -> Callable:
    """
    Prevents default warnings in tests (for e.g. when testing 404s)
    """

    def new_function(*args: Any, **kwargs: Any) -> None:
        """Raise logging level to error, execute original function, and reset logging level."""
        # raise logging level to ERROR
        logger: logging.Logger = logging.getLogger("django.request")
        previous_logging_level: int = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


def get_golden_dir() -> str:
    """Returns base path for test goldens."""
    return f"{os.getcwd()}/nutrition_tracker/tests/goldens/"
