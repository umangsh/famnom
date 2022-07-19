from __future__ import annotations

from django.test import TestCase
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_meal
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserMeal(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_MEAL_1 = test_objects.get_meal_today_1()
        cls.USER_MEAL_2 = test_objects.get_meal_today_2()
        cls.USER_MEAL_3 = test_objects.get_meal_yesterday_1()
        cls.USER_MEAL_4 = test_objects.get_meal_yesterday_2()

    def test_empty_qs(self):
        self.assertFalse(user_meal.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(4, user_meal._load_queryset(self.USER).count())

    def test_load_lmeal_no_params(self):
        self.assertIsNone(user_meal.load_lmeal(self.USER))

    def test_load_lmeal_id(self):
        self.assertEqual(self.USER_MEAL_1, user_meal.load_lmeal(self.USER, id_=self.USER_MEAL_1.id))

    def test_load_lmeal_external_id(self):
        self.assertEqual(self.USER_MEAL_2, user_meal.load_lmeal(self.USER, external_id=self.USER_MEAL_2.external_id))

    def test_load_lmeals_no_params(self):
        self.assertEqual(4, user_meal.load_lmeals(self.USER).count())

    def test_load_lmeals_ids(self):
        self.assertEqual(2, user_meal.load_lmeals(self.USER, ids=[self.USER_MEAL_1.id, self.USER_MEAL_2.id]).count())

    def test_load_lmeals_external_ids(self):
        self.assertEqual(
            2,
            user_meal.load_lmeals(
                self.USER, external_ids=[self.USER_MEAL_1.external_id, self.USER_MEAL_2.external_id]
            ).count(),
        )

    def test_load_lmeals_meal_date(self):
        self.assertEqual(2, user_meal.load_lmeals(self.USER, meal_date=timezone.localdate()).count())

    def test_load_lmeals_meal_date_order_by_num_days(self):
        qs = user_meal.load_lmeals(self.USER, order_by="-meal_date", meal_date=timezone.localdate(), num_days=2)
        self.assertEqual(4, qs.count())
        self.assertIn("-meal_date", qs.query.order_by)

    def test_load_lmeals_mixed_params(self):
        self.assertEqual(
            2,
            user_meal.load_lmeals(
                self.USER, ids=[self.USER_MEAL_1.id], external_ids=[self.USER_MEAL_2.external_id]
            ).count(),
        )

    def test_load_lmeals_mixed_params_2(self):
        self.assertEqual(
            1,
            user_meal.load_lmeals(
                self.USER, ids=[self.USER_MEAL_1.id], external_ids=[self.USER_MEAL_2.external_id], max_rows=1
            ).count(),
        )

    def test_load_latest_lmeal(self):
        self.assertEqual(self.USER_MEAL_2, user_meal.load_latest_lmeal(self.USER, timezone.localdate()))
        self.assertIsNone(user_meal.load_latest_lmeal(self.USER, timezone.localdate() - timezone.timedelta(2)))

    def test_create(self):
        user_meal.create(self.USER, meal_type=constants.MealType.BRUNCH)
        self.assertEqual(5, user_meal.load_lmeals(self.USER).count())

    def test_get_or_create(self):
        user_meal.get_or_create(self.USER, meal_type=constants.MealType.DINNER)
        self.assertEqual(5, user_meal.load_lmeals(self.USER).count())
        user_meal.get_or_create(self.USER, meal_type=constants.MealType.DINNER)
        self.assertEqual(5, user_meal.load_lmeals(self.USER).count())

    def test_update_or_create(self):
        user_meal.update_or_create(
            self.USER, defaults={"meal_type": constants.MealType.BRUNCH}, id=self.USER_MEAL_1.id
        )
        self.USER_MEAL_1.refresh_from_db()
        self.assertEqual(constants.MealType.BRUNCH, self.USER_MEAL_1.meal_type)

        user_meal.update_or_create(
            self.USER, defaults={"meal_type": constants.MealType.DINNER}, external_id=test_constants.TEST_UUID_3
        )
        self.assertEqual(5, user_meal.load_lmeals(self.USER).count())
