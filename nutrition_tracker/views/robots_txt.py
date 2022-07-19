"""robots.txt module"""
from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Serve robots.txt file."""
    lines = [
        "User-Agent: *",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
