from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.models import user_recipe
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserRecipe(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_RECIPE = test_objects.get_recipe()

    def test_empty_qs(self):
        self.assertFalse(user_recipe.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_recipe._load_queryset(self.USER).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        test_objects.get_user_2_recipe()
        self.assertEqual(2, user_recipe._load_queryset(self.USER).count())
        self.assertEqual(2, user_recipe._load_queryset(luser_2).count())

    def test_load_lrecipe_no_params(self):
        self.assertIsNone(user_recipe.load_lrecipe(self.USER))

    def test_load_lrecipe_id(self):
        self.assertEqual(self.USER_RECIPE, user_recipe.load_lrecipe(self.USER, id_=self.USER_RECIPE.id))

    def test_load_lrecipe_external_id(self):
        self.assertEqual(
            self.USER_RECIPE, user_recipe.load_lrecipe(self.USER, external_id=self.USER_RECIPE.external_id)
        )

    def test_load_lrecipes_no_params(self):
        self.assertEqual(1, user_recipe.load_lrecipes(self.USER).count())

    def test_load_lrecipes_ids(self):
        self.assertEqual(1, user_recipe.load_lrecipes(self.USER, ids=[self.USER_RECIPE.id]).count())

    def test_load_lrecipes_external_ids(self):
        self.assertEqual(1, user_recipe.load_lrecipes(self.USER, external_ids=[self.USER_RECIPE.external_id]).count())

    def test_load_lrecipes_all_params(self):
        self.assertEqual(
            1,
            user_recipe.load_lrecipes(
                self.USER, ids=[self.USER_RECIPE.id], external_ids=[self.USER_RECIPE.external_id]
            ).count(),
        )

    def test_load_lrecipes_for_browse_no_params(self):
        self.assertEqual(1, user_recipe.load_lrecipes_for_browse(self.USER).count())

    def test_load_lrecipes_for_browse_external_ids(self):
        self.assertEqual(
            1, user_recipe.load_lrecipes_for_browse(self.USER, external_ids=[self.USER_RECIPE.external_id]).count()
        )

    def test_load_lrecipes_for_browse_query(self):
        self.assertEqual(1, user_recipe.load_lrecipes_for_browse(self.USER, query="test").count())
        self.assertEqual(0, user_recipe.load_lrecipes_for_browse(self.USER, query="abcd").count())

    def test_create(self):
        user_recipe.create(self.USER, name="test123")
        self.assertEqual(2, user_recipe.load_lrecipes(self.USER).count())

    def test_get_or_create(self):
        user_recipe.get_or_create(self.USER, name="test123")
        self.assertEqual(2, user_recipe.load_lrecipes(self.USER).count())
        user_recipe.get_or_create(self.USER, name="test123")
        self.assertEqual(2, user_recipe.load_lrecipes(self.USER).count())

    def test_update_or_create(self):
        self.assertEqual("Test Recipe", self.USER_RECIPE.name)
        user_recipe.update_or_create(self.USER, defaults={"name": "test_123"}, id=self.USER_RECIPE.id)
        self.USER_RECIPE.refresh_from_db()
        self.assertEqual("test_123", self.USER_RECIPE.name)

        user_recipe.update_or_create(self.USER, defaults={"name": "test_456"}, external_id=test_constants.TEST_UUID_3)
        self.assertEqual(2, user_recipe.load_lrecipes(self.USER).count())
