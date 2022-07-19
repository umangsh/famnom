from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_preference, user_preference_threshold
from nutrition_tracker.tests import objects as test_objects


class TestLogicUserPrefs(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_load_nutrition_preferences_empty(self):
        self.assertFalse(user_prefs.load_nutrition_preferences(self.USER).exists())

    def test_load_nutrition_preferences(self):
        test_objects.get_nutrient_preference()
        self.assertEqual(1, user_prefs.load_nutrition_preferences(self.USER).count())

    def test_load_food_preferences_empty(self):
        self.assertFalse(user_prefs.load_food_preferences(self.USER).exists())

    def test_load_food_preferences(self):
        test_objects.get_user_preference()
        self.assertEqual(1, user_prefs.load_food_preferences(self.USER).count())

    def test_filter_preferences_by_id_empty(self):
        self.assertIsNone(user_prefs.filter_preferences_by_id([]))

    def test_filter_preferences_by_id(self):
        fp = test_objects.get_user_preference()
        np = test_objects.get_nutrient_preference()
        luser_preferences = user_preference.load_luser_preferences(self.USER)
        self.assertEqual(
            fp, user_prefs.filter_preferences_by_id(luser_preferences, food_external_id=fp.food_external_id)
        )
        self.assertEqual(
            np, user_prefs.filter_preferences_by_id(luser_preferences, food_nutrient_id=np.food_nutrient_id)
        )

    def test_filter_preferences_empty(self):
        self.assertEqual([], user_prefs.filter_preferences([]))

    def test_filter_preferences(self):
        fp = test_objects.get_user_preference()
        np = test_objects.get_nutrient_preference()
        luser_preferences = user_preference.load_luser_preferences(self.USER)
        self.assertEqual(
            [fp], user_prefs.filter_preferences(luser_preferences, flags_set=[user_preference.FLAG_IS_AVAILABLE])
        )
        self.assertEqual(
            [np], user_prefs.filter_preferences(luser_preferences, flags_unset=[user_preference.FLAG_IS_AVAILABLE])
        )
        self.assertEqual(
            [fp],
            user_prefs.filter_preferences(
                luser_preferences,
                flags_set_any=[user_preference.FLAG_IS_AVAILABLE, user_preference.FLAG_IS_NOT_ALLOWED],
            ),
        )

    def test_filter_food_preferences_empty(self):
        self.assertEqual([], user_prefs.filter_food_preferences([]))

    def test_filter_food_preferences(self):
        fp = test_objects.get_user_preference()
        test_objects.get_nutrient_preference()
        luser_preferences = user_preference.load_luser_preferences(self.USER)
        self.assertEqual([fp], user_prefs.filter_food_preferences(luser_preferences))

    def test_filter_category_preferences_empty(self):
        self.assertEqual([], user_prefs.filter_category_preferences([]))

    def test_filter_category_preferences(self):
        test_objects.get_user_preference()
        test_objects.get_nutrient_preference()
        cp = test_objects.get_category_preference()
        luser_preferences = user_preference.load_luser_preferences(self.USER)
        self.assertEqual([cp], user_prefs.filter_category_preferences(luser_preferences))

    def test_filter_nutrient_preferences_empty(self):
        self.assertEqual([], user_prefs.filter_nutrient_preferences([]))

    def test_filter_nutrient_preferences(self):
        test_objects.get_user_preference()
        np = test_objects.get_nutrient_preference()
        test_objects.get_category_preference()
        luser_preferences = user_preference.load_luser_preferences(self.USER)
        self.assertEqual([np], user_prefs.filter_nutrient_preferences(luser_preferences))

    def test_filter_preference_thresholds(self):
        self.assertIsNone(user_prefs.filter_preference_thresholds(user_preference_threshold.empty_qs()))
        fp = test_objects.get_user_preference()
        self.assertEqual(5, user_prefs.filter_preference_thresholds(fp.userpreferencethreshold_set.all()).min_value)

    def test_get_threshold_value(self):
        fp = test_objects.get_user_preference()
        self.assertEqual(5, user_prefs.get_threshold_value(fp))
