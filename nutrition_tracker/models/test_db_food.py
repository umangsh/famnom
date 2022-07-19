from __future__ import annotations

from django.test import TransactionTestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import db_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsDBFood(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.DB_FOOD = test_objects.get_db_food()
        self.DB_FOOD_2 = test_objects.get_db_food_2()

    def test_empty_qs(self):
        self.assertFalse(db_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(2, db_food._load_queryset().count())

    def test_load_cfood_no_params(self):
        self.assertIsNone(db_food.load_cfood())

    def test_load_cfood_id(self):
        self.assertEqual(self.DB_FOOD, db_food.load_cfood(id_=self.DB_FOOD.id))

    def test_load_cfood_external_id(self):
        self.assertEqual(self.DB_FOOD, db_food.load_cfood(external_id=self.DB_FOOD.external_id))

    def test_load_cfood_source_id_and_type(self):
        self.assertEqual(
            self.DB_FOOD, db_food.load_cfood(source_id=self.DB_FOOD.source_id, source_type=self.DB_FOOD.source_type)
        )

    def test_load_cfoods_no_params(self):
        self.assertEqual(2, db_food.load_cfoods().count())

    def test_load_cfoods_ids(self):
        self.assertEqual(1, db_food.load_cfoods(ids=[self.DB_FOOD.id]).count())

    def test_load_cfoods_external_ids(self):
        self.assertEqual(1, db_food.load_cfoods(external_ids=[self.DB_FOOD.external_id]).count())

    def test_load_cfoods_description(self):
        self.assertEqual(1, db_food.load_cfoods(description=self.DB_FOOD_2.description).count())

    def test_load_cfoods_source_type(self):
        self.assertEqual(2, db_food.load_cfoods(source_type=self.DB_FOOD.source_type).count())

    def test_load_cfoods_source_sub_type(self):
        self.assertEqual(1, db_food.load_cfoods(source_sub_type=self.DB_FOOD.source_sub_type).count())

    def test_load_cfoods_all_params(self):
        self.assertEqual(0, db_food.load_cfoods(ids=[self.DB_FOOD.id], description=self.DB_FOOD_2.description).count())

    def test_create(self):
        db_food.create(id=3, description="description")
        self.assertEqual(3, db_food.load_cfoods().count())

    def test_get_or_create(self):
        db_food.get_or_create(id=3, description="description")
        self.assertEqual(3, db_food.load_cfoods().count())
        db_food.get_or_create(id=3, description="description")
        self.assertEqual(3, db_food.load_cfoods().count())

    def test_update_or_create(self):
        self.assertEqual(constants.DBFoodSourceType.USDA, self.DB_FOOD_2.source_type)
        db_food.update_or_create(defaults={"source_type": constants.DBFoodSourceType.UNKNOWN}, id=self.DB_FOOD_2.id)
        self.DB_FOOD_2.refresh_from_db()
        self.assertEqual(constants.DBFoodSourceType.UNKNOWN, self.DB_FOOD_2.source_type)

        db_food.update_or_create(defaults={"description": "description"}, id=4)
        self.assertEqual(3, db_food.load_cfoods().count())

    def test_load_cfoods_iterator(self):
        DB_FOOD_3 = db_food.create(
            id=3,
            source_id=44,
            source_type=constants.DBFoodSourceType.USDA,
            source_sub_type=constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD,
        )
        iterator = db_food.load_cfoods_iterator()
        self.assertEqual(self.DB_FOOD, next(iterator))
        self.assertEqual(self.DB_FOOD_2, next(iterator))
        self.assertEqual(DB_FOOD_3, next(iterator))
        self.assertRaises(StopIteration, next, iterator)
