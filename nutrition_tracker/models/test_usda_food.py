from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import usda_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDAFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USDA_FOOD = test_objects.get_usda_food()
        cls.USDA_FOOD_2 = test_objects.get_usda_food_2()

    def test_empty_qs(self):
        self.assertFalse(usda_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(2, usda_food._load_queryset().count())

    def test_load_cfood_no_params(self):
        self.assertIsNone(usda_food.load_cfood())

    def test_load_cfood_fdc_id(self):
        self.assertEqual(self.USDA_FOOD, usda_food.load_cfood(fdc_id=self.USDA_FOOD.fdc_id))

    def test_load_cfood_external_id(self):
        self.assertEqual(self.USDA_FOOD, usda_food.load_cfood(external_id=self.USDA_FOOD.external_id))

    def test_load_cfoods_no_params(self):
        self.assertEqual(2, usda_food.load_cfoods().count())

    def test_load_cfoods_fdc_ids(self):
        self.assertEqual(1, usda_food.load_cfoods(fdc_ids=[self.USDA_FOOD.fdc_id]).count())

    def test_load_cfoods_external_ids(self):
        self.assertEqual(1, usda_food.load_cfoods(external_ids=[self.USDA_FOOD.external_id]).count())

    def test_load_cfoods_description(self):
        self.assertEqual(1, usda_food.load_cfoods(description=self.USDA_FOOD_2.description).count())

    def test_load_cfoods_data_type(self):
        self.assertEqual(1, usda_food.load_cfoods(data_types=[self.USDA_FOOD.data_type]).count())

    def test_load_cfoods_all_params(self):
        self.assertEqual(
            0, usda_food.load_cfoods(fdc_ids=[self.USDA_FOOD.fdc_id], description=self.USDA_FOOD_2.description).count()
        )

    def test_create(self):
        usda_food.create(fdc_id=3, description="description")
        self.assertEqual(3, usda_food.load_cfoods().count())

    def test_get_or_create(self):
        usda_food.get_or_create(fdc_id=3, description="description")
        self.assertEqual(3, usda_food.load_cfoods().count())
        usda_food.get_or_create(fdc_id=3, description="description")
        self.assertEqual(3, usda_food.load_cfoods().count())

    def test_update_or_create(self):
        self.assertIsNone(self.USDA_FOOD_2.data_type)
        usda_food.update_or_create(defaults={"data_type": "type"}, fdc_id=self.USDA_FOOD_2.fdc_id)
        self.USDA_FOOD_2.refresh_from_db()
        self.assertEqual("type", self.USDA_FOOD_2.data_type)

        usda_food.update_or_create(defaults={"description": "description"}, fdc_id=4)
        self.assertEqual(3, usda_food.load_cfoods().count())

    def test_load_cfoods_iterator(self):
        USDA_FOOD_3 = usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        iterator = usda_food.load_cfoods_iterator()
        self.assertEqual(self.USDA_FOOD, next(iterator))
        self.assertEqual(USDA_FOOD_3, next(iterator))
        self.assertRaises(StopIteration, next, iterator)

    def test_load_cfoods_iterator_with_start_no_rows(self):
        usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        qs = usda_food.load_cfoods_iterator(start=1)
        self.assertEqual(1, qs.count())

    def test_load_cfoods_iterator_no_start_with_rows(self):
        usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        qs = usda_food.load_cfoods_iterator(rows=1)
        self.assertEqual(1, qs.count())

    def test_load_cfoods_iterator_no_start_with_rows_more_than_total_foods(self):
        usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        qs = usda_food.load_cfoods_iterator(rows=6)
        self.assertEqual(2, qs.count())

    def test_load_cfoods_iterator_with_start_and_rows(self):
        usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        qs = usda_food.load_cfoods_iterator(start=1, rows=1)
        self.assertEqual(1, qs.count())

    def test_load_cfoods_iterator_with_data_type(self):
        USDA_FOOD_3 = usda_food.create(fdc_id=3, data_type=constants.USDA_FOUNDATION_FOOD)
        iterator = usda_food.load_cfoods_iterator(data_types=[constants.USDA_FOUNDATION_FOOD])
        self.assertEqual(USDA_FOOD_3, next(iterator))
        self.assertRaises(StopIteration, next, iterator)
