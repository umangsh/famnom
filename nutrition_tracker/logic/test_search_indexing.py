from __future__ import annotations

from unittest.mock import patch

from django.test import TransactionTestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import search_indexing
from nutrition_tracker.models import db_branded_food, db_food, search_result, usda_branded_food, usda_food
from nutrition_tracker.tests import objects as test_objects


class TestLogicSearchIndexing(TransactionTestCase):
    reset_sequences = True

    @patch(target="nutrition_tracker.logic.search_indexing.should_index_usda_foundation_food", return_value=False)
    def test_should_index_food_foundation_food_false(self, mock_method):
        cfood = test_objects.get_db_food_2()
        self.assertFalse(search_indexing.should_index_food(cfood))

    @patch(target="nutrition_tracker.logic.search_indexing.should_index_usda_foundation_food", return_value=True)
    def test_should_index_food_foundation_food_true(self, mock_method):
        cfood = test_objects.get_db_food_2()
        self.assertTrue(search_indexing.should_index_food(cfood))

    @patch(target="nutrition_tracker.logic.search_indexing.should_index_usda_branded_food", return_value=False)
    def test_should_index_food_branded_food_false(self, mock_method):
        cfood = test_objects.get_db_food()
        self.assertFalse(search_indexing.should_index_food(cfood))

    @patch(target="nutrition_tracker.logic.search_indexing.should_index_usda_branded_food", return_value=True)
    def test_should_index_food_branded_food_true(self, mock_method):
        cfood = test_objects.get_db_food()
        self.assertTrue(search_indexing.should_index_food(cfood))

    def test_should_index_usda_foundation_food_success_with_clash(self):
        cfood = test_objects.get_db_food()
        cfood.source_sub_type = constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD
        cfood.save()
        cfood.refresh_from_db()

        usda_food.get_or_create(
            fdc_id=cfood.source_id,
            description=cfood.description,
            data_type=constants.USDA_FOUNDATION_FOOD,
            publication_date="2022-04-02",
        )

        cfood_2 = test_objects.get_db_food_2()
        cfood_2.description = "test"
        cfood_2.save()
        cfood_2.refresh_from_db()

        usda_food.get_or_create(
            fdc_id=cfood_2.source_id,
            description=cfood_2.description,
            data_type=constants.USDA_FOUNDATION_FOOD,
            publication_date="2022-03-02",
        )

        self.assertTrue(search_indexing.should_index_usda_foundation_food(cfood))

    def test_should_index_usda_foundation_food_fails_with_clash(self):
        cfood = test_objects.get_db_food()
        cfood.source_sub_type = constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD
        cfood.save()
        cfood.refresh_from_db()

        usda_food.get_or_create(
            fdc_id=cfood.source_id,
            description=cfood.description,
            data_type=constants.USDA_FOUNDATION_FOOD,
            publication_date="2022-04-02",
        )

        cfood_2 = test_objects.get_db_food_2()
        cfood_2.description = "test"
        cfood_2.save()
        cfood_2.refresh_from_db()

        usda_food.get_or_create(
            fdc_id=cfood_2.source_id,
            description=cfood_2.description,
            data_type=constants.USDA_FOUNDATION_FOOD,
            publication_date="2022-03-02",
        )

        self.assertFalse(search_indexing.should_index_usda_foundation_food(cfood_2))

    def test_should_index_usda_branded_food_success_with_clash(self):
        cfood = test_objects.get_db_food()
        test_objects.get_db_branded_food()
        cfood = db_food.load_cfood(id_=cfood.id)

        cfood_usda, _ = usda_food.get_or_create(
            fdc_id=cfood.source_id, description=cfood.description, data_type=constants.USDA_BRANDED_FOOD
        )
        usda_branded_food.create(
            usda_food=cfood_usda,
            brand_name="brand",
            brand_owner="owner",
            gtin_upc="usda_upc",
            serving_size=50,
            serving_size_unit="g",
            household_serving_fulltext="4 cups",
            available_date="2022-04-04",
        )

        cfood_2 = test_objects.get_db_food_2()
        cfood_2.source_sub_type = constants.DBFoodSourceSubType.USDA_BRANDED_FOOD
        cfood_2.save()
        db_branded_food.create(db_food=cfood_2, brand_name="brand", gtin_upc="db_upc")

        cfood_usda_2, _ = usda_food.get_or_create(
            fdc_id=cfood_2.source_id, description=cfood_2.description, data_type=constants.USDA_BRANDED_FOOD
        )
        usda_branded_food.create(
            usda_food=cfood_usda_2,
            brand_name="brand",
            brand_owner="owner",
            gtin_upc="usda_upc",
            serving_size=50,
            serving_size_unit="g",
            household_serving_fulltext="4 cups",
            available_date="2022-03-04",
        )

        self.assertTrue(search_indexing.should_index_usda_branded_food(cfood))

    def test_should_index_usda_branded_food_fails_with_clash(self):
        cfood = test_objects.get_db_food()
        test_objects.get_db_branded_food()
        cfood = db_food.load_cfood(id_=cfood.id)

        cfood_usda, _ = usda_food.get_or_create(
            fdc_id=cfood.source_id, description=cfood.description, data_type=constants.USDA_BRANDED_FOOD
        )
        usda_branded_food.create(
            usda_food=cfood_usda,
            brand_name="brand",
            brand_owner="owner",
            gtin_upc="usda_upc",
            serving_size=50,
            serving_size_unit="g",
            household_serving_fulltext="4 cups",
            available_date="2022-04-04",
        )

        cfood_2 = test_objects.get_db_food_2()
        cfood_2.source_sub_type = constants.DBFoodSourceSubType.USDA_BRANDED_FOOD
        cfood_2.save()
        db_branded_food.create(db_food=cfood_2, brand_name="brand", gtin_upc="db_upc")

        cfood_usda_2, _ = usda_food.get_or_create(
            fdc_id=cfood_2.source_id, description=cfood_2.description, data_type=constants.USDA_BRANDED_FOOD
        )
        usda_branded_food.create(
            usda_food=cfood_usda_2,
            brand_name="brand",
            brand_owner="owner",
            gtin_upc="usda_upc",
            serving_size=50,
            serving_size_unit="g",
            household_serving_fulltext="4 cups",
            available_date="2022-03-04",
        )

        self.assertFalse(search_indexing.should_index_usda_branded_food(cfood_2))

    def test_convert_to_search_result(self):
        cfood = test_objects.get_db_food()
        test_objects.get_db_branded_food()
        return_value = search_indexing.convert_to_search_result(cfood)
        self.assertIsInstance(return_value, search_result.SearchResult)
        self.assertEqual(cfood.external_id, return_value.external_id)
        self.assertEqual(cfood.dbbrandedfood.brand_owner, return_value.brand_owner)

    def test_write_search_result(self):
        cfood = test_objects.get_db_food()
        test_objects.get_db_branded_food()
        srfood = search_indexing.convert_to_search_result(cfood)
        self.assertFalse(search_result.load_results().exists())

        search_indexing.write_search_result(srfood)
        self.assertEqual(1, search_result.load_results().count())

    def test_write_search_results_bulk(self):
        cfood = test_objects.get_db_food()
        test_objects.get_db_branded_food()
        cfood_2 = test_objects.get_db_food_2()
        srfood = search_indexing.convert_to_search_result(cfood)
        srfood_2 = search_indexing.convert_to_search_result(cfood_2)
        self.assertFalse(search_result.load_results().exists())

        search_indexing.write_search_results_bulk([srfood, srfood_2], constants.WRITE_BATCH_SIZE)
        self.assertEqual(2, search_result.load_results().count())
