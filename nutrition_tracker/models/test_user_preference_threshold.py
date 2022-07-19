from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import user_preference_threshold
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserPreferenceThreshold(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.PREFERENCE = test_objects.get_user_preference()

    def test_create(self):
        user_preference_threshold.create(self.USER, user_preference=self.PREFERENCE)

    def test_get_or_create(self):
        luser_preference_threshold, unused = user_preference_threshold.get_or_create(
            self.USER, user_preference=self.PREFERENCE
        )
