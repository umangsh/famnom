from __future__ import annotations

from crispy_forms.utils import render_crispy_form
from django.test import TestCase
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import LogForm
from nutrition_tracker.logic import food_portion
from nutrition_tracker.models import user_food_membership, user_meal, user_preference
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestFormsLogForm(TestCase):
    maxDiff = None

    def test_form_empty_init(self):
        kwargs = {"user": test_objects.get_user()}
        form = LogForm(**kwargs)

        with open("%s/test_form_log_empty.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = golden.read().replace("{TODAY_DATE}", str(timezone.localdate()))
            self.assertHTMLEqual(expected_output, render_crispy_form(form))

    def test_form_empty_init_food(self):
        kwargs = {
            "user": test_objects.get_user(),
            "lobject": test_objects.get_user_ingredient(),
            "lmeal": test_objects.get_meal_today_1(),
        }
        form = LogForm(**kwargs)
        self.assertIsNotNone(form.helper)

    def test_form_valid(self):
        lobject = test_objects.get_user_ingredient()
        kwargs = {
            "user": test_objects.get_user(),
            "lobject": lobject,
        }
        form = LogForm(
            data={
                "external_id": lobject.external_id,
                "meal_type": constants.MealType.BREAKFAST,
                "meal_date": timezone.localdate(),
                "quantity": 10,
                "serving": constants.ONE_SERVING_ID,
            },
            **kwargs,
        )
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        luser = test_objects.get_user()
        lobject = test_objects.get_user_ingredient()
        kwargs = {
            "user": luser,
            "lobject": lobject,
        }
        meal_date = timezone.localdate()
        form = LogForm(
            data={
                "external_id": lobject.external_id,
                "meal_type": constants.MealType.BREAKFAST,
                "meal_date": meal_date,
                "quantity": 10,
                "serving": constants.ONE_SERVING_ID,
            },
            **kwargs,
        )

        self.assertTrue(form.is_valid())

        form.save()
        lmeals = user_meal.load_lmeals(luser, meal_date=meal_date)
        self.assertEqual(1, lmeals.count())
        lmemberships = user_food_membership.load_lmemberships(luser)
        self.assertEqual(1, lmemberships.count())

    def test_form_save_update_availability(self):
        luser = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        lmembership = user_food_membership.load_lmemberships(luser)[0]
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)

        kwargs = {
            "user": luser,
            "lobject": lfood,
            "lmeal": lmeal,
            "lmembership": lmembership,
            "food_portions": food_portions,
        }
        form = LogForm(
            data={
                "external_id": lfood.external_id,
                "meal_type": lmeal.meal_type,
                "meal_date": lmeal.meal_date,
                "quantity": 10,
                "serving": constants.ONE_SERVING_ID,
                "is_available": True,
            },
            **kwargs,
        )

        self.assertTrue(form.is_valid())

        form.save()
        lmeals = user_meal.load_lmeals(luser)
        self.assertEqual(1, lmeals.count())
        lmemberships = user_food_membership.load_lmemberships(luser)
        self.assertEqual(1, lmemberships.count())
        self.assertEqual(10, lmemberships[0].portions[0].serving_size)
        luser_preference = user_preference.load_luser_preference(luser, food_external_id=lfood.external_id)
        self.assertTrue(luser_preference.is_available())

    def test_form_save_update_portion(self):
        luser = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        lmembership = user_food_membership.load_lmemberships(luser)[0]
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)

        kwargs = {
            "user": luser,
            "lobject": lfood,
            "lmeal": lmeal,
            "lmembership": lmembership,
            "food_portions": food_portions,
        }
        form = LogForm(
            data={
                "external_id": lfood.external_id,
                "meal_type": lmeal.meal_type,
                "meal_date": lmeal.meal_date,
                "quantity": 10,
                "serving": constants.ONE_SERVING_ID,
            },
            **kwargs,
        )

        self.assertTrue(form.is_valid())

        form.save()
        lmeals = user_meal.load_lmeals(luser)
        self.assertEqual(1, lmeals.count())
        lmemberships = user_food_membership.load_lmemberships(luser)
        self.assertEqual(1, lmemberships.count())
        self.assertEqual(10, lmemberships[0].portions[0].serving_size)

    def test_form_save_update_meal(self):
        luser = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        lfood_2 = test_objects.get_user_ingredient_2()
        ufm_2 = test_objects.get_user_food_membership(lmeal, lfood_2)
        test_objects.get_user_food_membership_portion(ufm_2)

        lmembership = user_food_membership.load_lmemberships(luser)[0]
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)

        kwargs = {
            "user": luser,
            "lobject": lfood,
            "lmeal": lmeal,
            "lmembership": lmembership,
            "food_portions": food_portions,
        }
        form = LogForm(
            data={
                "external_id": lfood.external_id,
                "meal_type": constants.MealType.LUNCH,
                "meal_date": timezone.localdate(),
                "quantity": 30,
                "serving": constants.ONE_SERVING_ID,
            },
            **kwargs,
        )

        self.assertTrue(form.is_valid())

        form.save()
        lmeals = user_meal.load_lmeals(luser)
        self.assertEqual(2, lmeals.count())
        lmemberships = user_food_membership.load_lmemberships(luser)
        self.assertEqual(2, lmemberships.count())

    def test_form_save_update_meal_delete_old_meal(self):
        luser = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership_portion(ufm)

        lmembership = user_food_membership.load_lmemberships(luser)[0]
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)

        kwargs = {
            "user": luser,
            "lobject": lfood,
            "lmeal": lmeal,
            "lmembership": lmembership,
            "food_portions": food_portions,
        }
        form = LogForm(
            data={
                "external_id": lfood.external_id,
                "meal_type": constants.MealType.LUNCH,
                "meal_date": timezone.localdate(),
                "quantity": 30,
                "serving": constants.ONE_SERVING_ID,
            },
            **kwargs,
        )

        self.assertTrue(form.is_valid())

        form.save()
        lmeals = user_meal.load_lmeals(luser)
        self.assertEqual(1, lmeals.count())
        lmemberships = user_food_membership.load_lmemberships(luser)
        self.assertEqual(1, lmemberships.count())
        self.assertEqual(30, lmemberships[0].portions[0].serving_size)
