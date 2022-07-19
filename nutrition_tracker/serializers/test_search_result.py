from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import SearchResultSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersSearchResult(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SEARCH_RESULT = test_objects.get_search_result_1()
        cls.SERIALIZED_SEARCH_RESULT = SearchResultSerializer(instance=cls.SEARCH_RESULT)

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(set(data.keys()), {"external_id", "dname", "url", "brand_name", "brand_owner"})

    def test_external_id_content(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(data["external_id"], self.SEARCH_RESULT.external_id)

    def test_url_content(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(data["url"], "/my_food/%s/" % self.SEARCH_RESULT.external_id)

    def test_display_name_content(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(data["dname"], "search_result_1")

    def test_brand_name_content(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(data["brand_name"], "brand_name")

    def test_brand_owner_content(self):
        data = self.SERIALIZED_SEARCH_RESULT.data
        self.assertEqual(data["brand_owner"], "brand_owner")
