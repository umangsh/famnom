from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from nutrition_tracker.models import search_result
from nutrition_tracker.tests import objects as test_objects


class TestCommandSearchIndexer(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.get_search_result_1()
        test_objects.get_search_result_2()
        test_objects.get_db_food()
        test_objects.get_db_branded_food()

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("search_indexer", *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()

    def test_dry_run(self):
        self.call_command(dry_run=True)
        qs = search_result.load_results()
        self.assertEqual(2, qs.count())

    def test_search_indexer(self):
        self.call_command()
        qs = search_result.load_results()
        self.assertEqual(1, qs.count())
        self.assertEqual("'brand':2 'db':4 'owner':3 'test':1 'upc':5", qs[0].search_vector)

    @patch(target="nutrition_tracker.logic.search_indexing.should_index_food", return_value=False)
    def test_search_indexer_skipped_result(self, mock_should_index_food):
        self.call_command()
        qs = search_result.load_results()
        self.assertEqual(0, qs.count())
