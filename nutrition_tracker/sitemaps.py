"""Sitemaps module."""
from __future__ import annotations

from typing import Any

from django.contrib.sitemaps import Sitemap
from django.urls import reverse_lazy

from nutrition_tracker.constants import constants


class StaticSitemap(Sitemap):
    """Static page configuration."""

    changefreq = "yearly"
    priority = 1.0
    protocol = "https"

    def items(self) -> list[str]:
        return [
            constants.URL_HOME,
            "account_login",
            "account_signup",
            "cookie_policy",
            "privacy_policy",
            "terms_of_use",
        ]

    def location(self, item: Any) -> str:
        return reverse_lazy(item)
