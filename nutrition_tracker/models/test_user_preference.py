from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_preference
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserPreference(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.PREFERENCE = test_objects.get_user_preference()

    def test_empty_qs(self):
        self.assertFalse(user_preference.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_preference._load_queryset(self.PREFERENCE.user).count())

    def test_load_luser_preference(self):
        self.assertEqual(
            self.PREFERENCE,
            user_preference.load_luser_preference(
                self.PREFERENCE.user, food_external_id=self.PREFERENCE.food_external_id
            ),
        )

    def test_load_luser_preferences(self):
        self.assertEqual(
            1,
            user_preference.load_luser_preferences(
                self.PREFERENCE.user, food_external_ids=[self.PREFERENCE.food_external_id]
            ).count(),
        )

    def test_create(self):
        user_preference.create(self.USER, food_nutrient_id=constants.ENERGY_NUTRIENT_ID)
        self.assertEqual(2, user_preference.load_luser_preferences(self.USER).count())

    def test_get_flags(self):
        self.assertEqual(1, user_preference.get_flags({user_preference.FLAG_IS_NOT_ALLOWED: True}))
        self.assertEqual(
            3,
            user_preference.get_flags(
                {
                    user_preference.FLAG_IS_NOT_ALLOWED: True,
                    user_preference.FLAG_IS_AVAILABLE: True,
                }
            ),
        )

    def test_get_flag(self):
        self.assertFalse(self.PREFERENCE.get_flag(user_preference.FLAG_IS_NOT_ALLOWED))

    def test_add_flag(self):
        self.assertFalse(self.PREFERENCE.is_not_allowed())
        self.PREFERENCE.add_flag(user_preference.FLAG_IS_NOT_ALLOWED)
        self.assertTrue(self.PREFERENCE.is_not_allowed())

    def test_remove_flag(self):
        self.PREFERENCE.add_flag(user_preference.FLAG_IS_NOT_ALLOWED)
        self.assertTrue(self.PREFERENCE.is_not_allowed())
        self.PREFERENCE.remove_flag(user_preference.FLAG_IS_NOT_ALLOWED)
        self.assertFalse(self.PREFERENCE.is_not_allowed())

    def test_update_flag(self):
        self.assertFalse(self.PREFERENCE.is_not_allowed())
        self.PREFERENCE.update_flag(user_preference.FLAG_IS_NOT_ALLOWED, True)
        self.assertTrue(self.PREFERENCE.is_not_allowed())
        self.PREFERENCE.update_flag(user_preference.FLAG_IS_NOT_ALLOWED, False)
        self.assertFalse(self.PREFERENCE.is_not_allowed())
