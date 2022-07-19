from __future__ import annotations

from django.contrib.postgres.search import SearchVector
from django.test import TestCase

from nutrition_tracker.models import search_result
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestModelsSearchResult(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SEARCH_RESULT_1 = test_objects.get_search_result_1()
        cls.SEARCH_RESULT_2 = test_objects.get_search_result_2()

    def test_display_brand_details(self):
        self.assertEqual("brand_name, brand_owner", self.SEARCH_RESULT_1.display_brand_details)

    def test_empty_qs(self):
        self.assertFalse(search_result.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(2, search_result._load_queryset().count())

    def test_load_results_no_params(self):
        self.assertEqual(2, search_result.load_results().count())

    def test_load_results_ids(self):
        self.assertEqual(2, search_result.load_results(ids=[self.SEARCH_RESULT_1.id, self.SEARCH_RESULT_2.id]).count())

    def test_load_results_external_ids(self):
        self.assertEqual(
            2,
            search_result.load_results(
                external_ids=[self.SEARCH_RESULT_1.external_id, self.SEARCH_RESULT_2.external_id]
            ).count(),
        )

    def test_load_results_gtin_upc(self):
        self.assertEqual(1, search_result.load_results(gtin_upc="gtin_upc").count())

    def test_load_results_all_params(self):
        self.assertEqual(
            2,
            search_result.load_results(
                ids=[self.SEARCH_RESULT_1.id],
                external_ids=[self.SEARCH_RESULT_2.external_id],
                gtin_upc="upcdoesnotexist",
            ).count(),
        )

    def test_bulk_create(self):
        SEARCH_RESULT_BULK_1 = search_result.SearchResult(external_id=test_constants.TEST_UUID_3)
        SEARCH_RESULT_BULK_2 = search_result.SearchResult(external_id=test_constants.TEST_UUID_4)
        search_result.bulk_create([SEARCH_RESULT_BULK_1, SEARCH_RESULT_BULK_2])
        self.assertEqual(4, search_result.load_results().count())

    def test_create(self):
        SEARCH_RESULT_3 = search_result.create(external_id=test_constants.TEST_UUID_3)
        self.assertEqual(1, search_result.load_results(ids=[SEARCH_RESULT_3.id]).count())

    def test_update(self):
        self.assertEqual("search_result_1", self.SEARCH_RESULT_1.name)
        self.assertEqual("search_result_2", self.SEARCH_RESULT_2.name)
        search_result.update(name="test")
        self.SEARCH_RESULT_1.refresh_from_db()
        self.assertEqual("test", self.SEARCH_RESULT_1.name)
        self.SEARCH_RESULT_2.refresh_from_db()
        self.assertEqual("test", self.SEARCH_RESULT_2.name)

    def test_get_search_vector(self):
        expected_search_vector = (
            SearchVector("name", config="english")
            + SearchVector("brand_name", config="english")
            + SearchVector("brand_owner", config="english")
            + SearchVector("subbrand_name", config="english")
            + SearchVector("gtin_upc", config="english")
        )
        self.assertEqual(expected_search_vector, search_result.get_search_vector())

    def test_update_search_vector(self):
        self.assertIsNone(self.SEARCH_RESULT_1.search_vector)
        self.assertIsNone(self.SEARCH_RESULT_2.search_vector)
        search_result.update_search_vector()
        self.SEARCH_RESULT_1.refresh_from_db()
        self.assertEqual(
            "'1':3 'brand':4,6 'gtin':8 'name':5 'owner':7 'result':2 'search':1 'upc':9",
            self.SEARCH_RESULT_1.search_vector,
        )
        self.SEARCH_RESULT_2.refresh_from_db()
        self.assertEqual("'2':3 'result':2 'search':1", self.SEARCH_RESULT_2.search_vector)

    def test_delete_all(self):
        search_result.delete_all()
        self.assertEqual(0, search_result.load_results().count())

    def test_url(self):
        expected_url = "/my_food/%s/" % self.SEARCH_RESULT_1.external_id
        self.assertEqual(expected_url, self.SEARCH_RESULT_1.url)

    def test_display_name(self):
        self.assertEqual("search_result_1", self.SEARCH_RESULT_1.display_name)
        self.SEARCH_RESULT_1.name = "teST"
        # Invalidate the previously cached cached_property
        del self.SEARCH_RESULT_1.display_name
        self.assertEqual("teST", self.SEARCH_RESULT_1.display_name)
