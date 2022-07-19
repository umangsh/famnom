"""Utility methods for Views."""
from __future__ import annotations

from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar, cast

from django.http import HttpRequest, JsonResponse


def is_ajax(request: HttpRequest) -> bool:
    """Returns true for ajax requests."""
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def ajax_login_required(function: FuncT) -> FuncT:
    """Login required decorator for ajax views."""

    @wraps(function)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Return unauthorized access for logged out ajax requests when using this decorator."""
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        return JsonResponse({}, status=HTTPStatus.UNAUTHORIZED)

    return cast(FuncT, wrapper)
