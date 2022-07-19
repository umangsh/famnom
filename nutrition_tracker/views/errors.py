"""View errors module."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class NotFoundErrorView(TemplateView):
    """404 view."""

    template_name: str = "errors/404.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response: HttpResponse = super().get(request, *args, **kwargs)
        response.status_code = HTTPStatus.NOT_FOUND
        return response


def handler500(request: HttpRequest) -> HttpResponse:
    """500 view."""
    return render(request, "errors/500.html", status=HTTPStatus.INTERNAL_SERVER_ERROR)
