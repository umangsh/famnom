from __future__ import annotations

from django.test import TestCase


class TestSitemaps(TestCase):
    def test_static_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertTrue("accounts/login/" in response.content.decode("utf-8"))
        self.assertTrue("privacy_policy/" in response.content.decode("utf-8"))
