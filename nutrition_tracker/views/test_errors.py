from __future__ import annotations

from http import HTTPStatus

from django.test import SimpleTestCase

from nutrition_tracker.tests import utils as test_utils


class TestViewsErrors(SimpleTestCase):
    @test_utils.prevent_request_warnings
    def test_404(self):
        response = self.client.get("/doesnotexist/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")
        self.assertContains(response, "Page Not Found", status_code=HTTPStatus.NOT_FOUND)
