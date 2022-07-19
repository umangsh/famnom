from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.logic import search
from nutrition_tracker.tests import objects as test_objects


class TestLogicSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.index_cfood()

    def test_empty_query(self):
        self.assertFalse(search.search("").exists())

    def test_query_not_found(self):
        self.assertFalse(search.search("unknownfood").exists())

    def test_query(self):
        self.assertEqual(1, search.search("test").count())
        self.assertEqual(1, search.search("brand").count())
        self.assertEqual(1, search.search("owner").count())
        self.assertEqual(1, search.search("db_upc").count())

    def test_search_barcode_not_found(self):
        self.assertFalse(search.search_barcode("unknownbarcode").exists())

    def test_search_barcode(self):
        self.assertEqual(1, search.search_barcode("db_upc").count())
