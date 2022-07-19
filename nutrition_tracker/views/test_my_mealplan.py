from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_food_membership, user_meal, user_preference
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestViewsMyMealplan(TestCase):
    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_mealplan"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_mealplan/")

    def test_logged_in_step_one_success(self):
        test_objects.get_user()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_mealplan"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_mealplan_one.html")

    def test_logged_in_step_one_submit(self):
        luser = test_objects.get_user()
        lfood_1 = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lrecipe_1 = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_mealplan"),
            {
                "available_foods": ["%s" % lfood_1.external_id, "%s" % lfood_2.external_id],
                "available_recipes": "%s" % lrecipe_1.external_id,
                "must_have_foods": "%s" % lfood_1.external_id,
                "dont_have_recipes": "%s" % lrecipe_2.external_id,
                "dont_repeat_foods": "%s" % lfood_2.external_id,
                "dont_repeat_recipes": ["%s" % lrecipe_1.external_id, "%s" % lrecipe_2.external_id],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_mealplan/2/")
        luser_preferences = list(user_prefs.load_food_preferences(luser))
        self.assertEqual(
            3, len(user_prefs.filter_preferences(luser_preferences, flags_set=[user_preference.FLAG_IS_AVAILABLE]))
        )
        self.assertEqual(
            2,
            len(
                user_prefs.filter_preferences(
                    luser_preferences,
                    flags_unset=[user_preference.FLAG_IS_NOT_ALLOWED, user_preference.FLAG_IS_NOT_ZEROABLE],
                )
            ),
        )
        self.assertEqual(
            4,
            len(
                user_prefs.filter_preferences(
                    luser_preferences,
                    flags_set_any=[user_preference.FLAG_IS_AVAILABLE, user_preference.FLAG_IS_NOT_REPEATABLE],
                )
            ),
        )

    def test_logged_in_step_two_success(self):
        test_objects.get_user()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_mealplan", kwargs={"step": 2}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_mealplan_two.html")

    def test_logged_in_step_two_submit(self):
        luser = test_objects.get_user()
        lfood_1 = test_objects.get_user_ingredient()
        test_objects.get_user_preference()
        lfood_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_preference_2()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_mealplan", kwargs={"step": 2}),
            {
                form_utils.get_field_name(lfood_1.external_id): 53,
                form_utils.get_threshold_field_name(lfood_1.external_id): constants.Threshold.MAX_VALUE,
                form_utils.get_field_name(lfood_2.external_id): 84,
                form_utils.get_threshold_field_name(lfood_2.external_id): constants.Threshold.EXACT_VALUE,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_mealplan/3/")
        luser_preferences = list(user_prefs.load_food_preferences(luser))
        luser_preference_1 = user_prefs.filter_preferences_by_id(
            luser_preferences, food_external_id=lfood_1.external_id
        )
        threshold = luser_preference_1.userpreferencethreshold_set.all().first()
        self.assertIsNone(threshold.min_value)
        self.assertEqual(53, threshold.max_value)
        self.assertIsNone(threshold.exact_value)

        luser_preference_2 = user_prefs.filter_preferences_by_id(
            luser_preferences, food_external_id=lfood_2.external_id
        )
        threshold = luser_preference_2.userpreferencethreshold_set.all().first()
        self.assertIsNone(threshold.min_value)
        self.assertIsNone(threshold.max_value)
        self.assertEqual(84, threshold.exact_value)

    def test_logged_in_step_three_success(self):
        test_objects.get_user()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_mealplan", kwargs={"step": 3}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_mealplan_three.html")

    def test_logged_in_step_three_submit(self):
        luser = test_objects.get_user()
        lfood_1 = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lrecipe_1 = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_mealplan", kwargs={"step": 3}),
            {
                form_utils.get_field_name(lfood_1.external_id): 53,
                form_utils.get_meal_field_name(lfood_1.external_id): constants.MealType.BREAKFAST,
                form_utils.get_field_name(lfood_2.external_id): 19,
                form_utils.get_meal_field_name(lfood_2.external_id): constants.MealType.LUNCH,
                form_utils.get_field_name(lrecipe_1.external_id): 24,
                form_utils.get_meal_field_name(lrecipe_1.external_id): "",
                form_utils.get_field_name(lrecipe_2.external_id): 112,
                form_utils.get_meal_field_name(lrecipe_2.external_id): constants.MealType.BREAKFAST,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_MEALPLAN_SAVE, messages)
        self.assertEqual(2, user_meal.load_lmeals(luser, meal_date=timezone.localdate()).count())
        self.assertEqual(3, user_food_membership.load_lmemberships(luser).count())

    def test_logged_in_step_three_submit_no_items_saved(self):
        luser = test_objects.get_user()
        lfood_1 = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lrecipe_1 = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_mealplan", kwargs={"step": 3}),
            {
                form_utils.get_field_name(lfood_1.external_id): 53,
                form_utils.get_meal_field_name(lfood_1.external_id): "",
                form_utils.get_field_name(lfood_2.external_id): 19,
                form_utils.get_meal_field_name(lfood_2.external_id): "",
                form_utils.get_field_name(lrecipe_1.external_id): 24,
                form_utils.get_meal_field_name(lrecipe_1.external_id): "",
                form_utils.get_field_name(lrecipe_2.external_id): 112,
                form_utils.get_meal_field_name(lrecipe_2.external_id): "",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_INFO_MEALPLAN_NOT_SAVED, messages)
        self.assertEqual(0, user_meal.load_lmeals(luser, meal_date=timezone.localdate()).count())
        self.assertEqual(0, user_food_membership.load_lmemberships(luser).count())
