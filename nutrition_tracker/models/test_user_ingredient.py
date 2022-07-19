from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.models import user_ingredient
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserIngredient(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()

    def test_display_name(self):
        self.assertEqual("test", self.USER_INGREDIENT.display_name)

    def test_display_brand_name(self):
        test_objects.get_user_branded_food()
        self.USER_INGREDIENT = user_ingredient.load_lfood(self.USER, id_=self.USER_INGREDIENT.id)
        self.assertEqual("brand", self.USER_INGREDIENT.display_brand_field("brand_name"))

    def test_display_sub_brand_name(self):
        test_objects.get_user_branded_food()
        self.USER_INGREDIENT = user_ingredient.load_lfood(self.USER, id_=self.USER_INGREDIENT.id)
        self.assertEqual("", self.USER_INGREDIENT.display_brand_field("subbrand_name"))

    def test_display_brand_details(self):
        test_objects.get_user_branded_food()
        self.USER_INGREDIENT = user_ingredient.load_lfood(self.USER, id_=self.USER_INGREDIENT.id)
        self.assertEqual("brand, owner", self.USER_INGREDIENT.display_brand_details)

    def test_empty_qs(self):
        self.assertFalse(user_ingredient.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(2, user_ingredient._load_queryset(self.USER).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        test_objects.get_user_2_ingredient()
        test_objects.get_user_2_ingredient_2()
        self.assertEqual(4, user_ingredient._load_queryset(self.USER).count())
        self.assertEqual(4, user_ingredient._load_queryset(luser_2).count())

    def test_filter_duplicate_db_foods_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        test_objects.get_user_2_ingredient()
        test_objects.get_user_2_ingredient_2()

        qs = user_ingredient._load_queryset(self.USER)
        self.assertEqual(3, user_ingredient._filter_duplicate_db_foods(self.USER, qs).count())

        qs = user_ingredient._load_queryset(luser_2)
        self.assertEqual(3, user_ingredient._filter_duplicate_db_foods(luser_2, qs).count())

    def test_load_lfood_no_params(self):
        self.assertIsNone(user_ingredient.load_lfood(self.USER))

    def test_load_lfood_id(self):
        self.assertEqual(self.USER_INGREDIENT, user_ingredient.load_lfood(self.USER, id_=self.USER_INGREDIENT.id))

    def test_load_lfood_external_id(self):
        self.assertEqual(
            self.USER_INGREDIENT, user_ingredient.load_lfood(self.USER, external_id=self.USER_INGREDIENT.external_id)
        )

    def test_load_lfood_fdc_id(self):
        self.assertEqual(
            self.USER_INGREDIENT, user_ingredient.load_lfood(self.USER, db_food_id=self.USER_INGREDIENT.db_food.id)
        )

    def test_load_lfoods_no_params(self):
        self.assertEqual(2, user_ingredient.load_lfoods(self.USER).count())

    def test_load_lfoods_ids(self):
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER, ids=[self.USER_INGREDIENT.id]).count())

    def test_load_lfoods_external_ids(self):
        self.assertEqual(
            1, user_ingredient.load_lfoods(self.USER, external_ids=[self.USER_INGREDIENT_2.external_id]).count()
        )

    def test_load_lfoods_db_food_ids(self):
        self.assertEqual(
            1, user_ingredient.load_lfoods(self.USER, db_food_ids=[self.USER_INGREDIENT.db_food.id]).count()
        )

    def test_load_lfoods_all_params(self):
        self.assertEqual(
            2,
            user_ingredient.load_lfoods(
                self.USER, ids=[self.USER_INGREDIENT.id], external_ids=[self.USER_INGREDIENT_2.external_id]
            ).count(),
        )

    def test_load_lfoods_for_browse_no_params(self):
        self.assertEqual(2, user_ingredient.load_lfoods_for_browse(self.USER).count())

    def test_load_lfoods_for_browse_external_ids(self):
        self.assertEqual(
            1,
            user_ingredient.load_lfoods_for_browse(
                self.USER, external_ids=[self.USER_INGREDIENT_2.external_id]
            ).count(),
        )

    def test_load_lfoods_for_browse_query(self):
        self.assertEqual(2, user_ingredient.load_lfoods_for_browse(self.USER, query="TEST").count())

    def test_load_lfoods_for_browse_user_brand_name(self):
        test_objects.get_user_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="brand").count())

    def test_load_lfoods_for_browse_db_brand_name(self):
        test_objects.get_db_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="brand").count())

    def test_load_lfoods_for_browse_user_and_db_brand_name_fails(self):
        test_objects.get_user_branded_food()
        test_objects.get_db_branded_food()
        self.assertEqual(0, user_ingredient.load_lfoods_for_browse(self.USER, query="fails").count())

    def test_load_lfoods_for_browse_user_brand_owner(self):
        test_objects.get_user_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="owner").count())

    def test_load_lfoods_for_browse_db_brand_owner(self):
        test_objects.get_db_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="owner").count())

    def test_load_lfoods_for_browse_user_and_db_brand_owner_fails(self):
        test_objects.get_user_branded_food()
        test_objects.get_db_branded_food()
        self.assertEqual(0, user_ingredient.load_lfoods_for_browse(self.USER, query="fails").count())

    def test_load_lfoods_for_browse_user_gtin_upc(self):
        test_objects.get_user_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="user_upc").count())

    def test_load_lfoods_for_browse_db_gtin_upc(self):
        test_objects.get_db_branded_food()
        self.assertEqual(1, user_ingredient.load_lfoods_for_browse(self.USER, query="db_upc").count())

    def test_load_lfoods_for_browse_user_and_db_gtin_upc_fails(self):
        test_objects.get_user_branded_food()
        test_objects.get_db_branded_food()
        self.assertEqual(0, user_ingredient.load_lfoods_for_browse(self.USER, query="fails").count())

    def test_create(self):
        user_ingredient.create(self.USER, name="test123")
        self.assertEqual(3, user_ingredient.load_lfoods(self.USER).count())

    def test_get_or_create(self):
        user_ingredient.get_or_create(self.USER, name="test123")
        self.assertEqual(3, user_ingredient.load_lfoods(self.USER).count())
        user_ingredient.get_or_create(self.USER, name="test123")
        self.assertEqual(3, user_ingredient.load_lfoods(self.USER).count())

    def test_update_or_create(self):
        self.assertEqual("test_2", self.USER_INGREDIENT_2.name)
        user_ingredient.update_or_create(self.USER, defaults={"name": "test_123"}, id=self.USER_INGREDIENT_2.id)
        self.USER_INGREDIENT_2.refresh_from_db()
        self.assertEqual("test_123", self.USER_INGREDIENT_2.name)
        self.assertEqual("test", self.USER_INGREDIENT.name)

        user_ingredient.update_or_create(
            self.USER, defaults={"name": "test_123"}, external_id=test_constants.TEST_UUID_3
        )
        self.assertEqual(3, user_ingredient.load_lfoods(self.USER).count())
