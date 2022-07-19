from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserFoodMembership(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.INGREDIENT = test_objects.get_user_ingredient()
        cls.RECIPE = test_objects.get_recipe()
        cls.MEMBERSHIP = test_objects.get_user_food_membership(cls.RECIPE, cls.INGREDIENT)

    def test_empty_qs(self):
        self.assertFalse(user_food_membership.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_food_membership._load_queryset(self.USER).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        luser_2.refresh_from_db()
        self.assertEqual(1, user_food_membership._load_queryset(luser_2).count())

    def test_load_lmembership_no_params(self):
        self.assertIsNone(user_food_membership.load_lmembership(self.USER))

    def test_load_lmembership_id(self):
        self.assertEqual(self.MEMBERSHIP, user_food_membership.load_lmembership(self.USER, id_=self.MEMBERSHIP.id))

    def test_load_lmembership_external_id(self):
        self.assertEqual(
            self.MEMBERSHIP, user_food_membership.load_lmembership(self.USER, external_id=self.MEMBERSHIP.external_id)
        )

    def test_load_lmemberships_no_params(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_food_membership.load_lmemberships(user).count())

    def test_load_lmemberships_ids(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_food_membership.load_lmemberships(user, ids=[self.MEMBERSHIP.id]).count())

    def test_load_lmemberships_external_ids(self):
        user = test_objects.get_user()
        self.assertEqual(
            1, user_food_membership.load_lmemberships(user, external_ids=[self.MEMBERSHIP.external_id]).count()
        )

    def test_load_lmemberships_parent_child(self):
        user = test_objects.get_user()
        self.assertEqual(
            self.MEMBERSHIP,
            user_food_membership.load_lmemberships(
                user,
                parent_id=self.RECIPE.id,
                parent_type_id=data_loaders.get_content_type_recipe_id(),
                child_id=self.INGREDIENT.id,
                child_type_id=data_loaders.get_content_type_ingredient_id(),
            ).first(),
        )

    def test_create(self):
        user = test_objects.get_user()
        user_food_membership.create(user, parent=self.RECIPE, child=test_objects.get_user_ingredient_2())
        self.assertEqual(2, user_food_membership.load_lmemberships(user).count())

    def test_update_or_create(self):
        user = test_objects.get_user()
        child = test_objects.get_user_ingredient_2()
        user_food_membership.update_or_create(
            user,
            defaults={},
            parent_id=self.RECIPE.id,
            parent_type_id=data_loaders.get_content_type_recipe_id(),
            child_id=child.id,
            child_type_id=data_loaders.get_content_type_ingredient_id(),
        )
        self.assertEqual(2, user_food_membership.load_lmemberships(user).count())
