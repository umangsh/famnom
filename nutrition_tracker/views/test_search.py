from __future__ import annotations

import json
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.tests import objects as test_objects


class TestViewsSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.index_cfood()

    def test_get_results_empty_query(self):
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertQuerysetEqual(response.context["search_results"], [])

    def test_get_results_exact_query_match(self):
        url = "{}?q={}".format(reverse("search"), "test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["search_results"].count())

    def test_get_results_query_match(self):
        url = "{}?q={}".format(reverse("search"), "tESt")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["search_results"].count())

    def test_get_results_query_no_match(self):
        url = "{}?q={}".format(reverse("search"), "nomatch")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertQuerysetEqual(response.context["search_results"], [])

    def test_get_results_exact_query_match_ajax(self):
        url = "{}?q={}".format(reverse("search"), "test")
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, len(json.loads(response.content.decode("utf8"))))
