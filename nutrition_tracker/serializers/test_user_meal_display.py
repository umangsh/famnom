from __future__ import annotations

from django.test import RequestFactory, TestCase
from django.utils import timezone
from rest_framework.renderers import JSONRenderer
from rest_framework.test import force_authenticate

from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import UserMealDisplaySerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserMealDisplay(TestCase):
    @classmethod
    def setUpTestData(cls):
        request = RequestFactory().get("/")
        request.user = test_objects.get_user()
        force_authenticate(request, user=request.user)

        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        ufmp = test_objects.get_user_food_membership_portion(ufm)

        lrecipe_2 = test_objects.get_recipe_2()
        ufm2 = test_objects.get_user_food_membership(lmeal, lrecipe_2)
        ufm2p = test_objects.get_user_food_membership_portion(ufm2)

        cls.USER_INGREDIENT = lfood
        cls.USER_INGREDIENT_MEMBERSHIP = ufm
        cls.USER_INGREDIENT_MEMBERSHIP_PORTION = ufmp
        cls.USER_MEMBER_RECIPE = lrecipe_2
        cls.USER_MEMBER_RECIPE_MEMBERSHIP = ufm2
        cls.USER_MEMBER_RECIPE_MEMBERSHIP_PORTION = ufm2p
        cls.USER_MEAL = user_meal.load_lmeal(request.user, external_id=lmeal.external_id)
        cls.SERIALIZED_USER_MEAL = UserMealDisplaySerializer(instance=cls.USER_MEAL, context={"request": request})

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertEqual(
            set(data.keys()),
            {
                "external_id",
                "meal_type",
                "meal_date",
                "display_nutrients",
                "member_ingredients",
                "member_recipes",
            },
        )

    def test_external_id_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertEqual(data["external_id"], str(self.USER_MEAL.external_id))

    def test_meal_type_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertEqual(data["meal_type"], self.USER_MEAL.meal_type)

    def test_meal_date_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertEqual(data["meal_date"], str(self.USER_MEAL.meal_date))

    def test_nutrients_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertJSONEqual(
            JSONRenderer().render(data["display_nutrients"]),
            {
                "values": [
                    {"id": 1008, "name": "Calories", "amount": 50.0, "unit": "kcal"},
                    {"id": 1004, "name": "Total Fat", "amount": None, "unit": "g"},
                    {"id": 1258, "name": "Saturated Fat", "amount": None, "unit": "g"},
                    {"id": 1257, "name": "Trans Fat", "amount": None, "unit": "g"},
                    {"id": 1293, "name": "Polyunsaturated Fat", "amount": None, "unit": "g"},
                    {"id": 1292, "name": "Monounsaturated Fat", "amount": None, "unit": "g"},
                    {"id": 1253, "name": "Cholesterol", "amount": None, "unit": "mg"},
                    {"id": 1093, "name": "Sodium", "amount": None, "unit": "mg"},
                    {"id": 1099, "name": "Fluoride", "amount": None, "unit": "mcg"},
                    {"id": 1005, "name": "Total Carbohydrate", "amount": None, "unit": "g"},
                    {"id": 1079, "name": "Dietary Fiber", "amount": None, "unit": "g"},
                    {"id": 1082, "name": "Soluble Fiber", "amount": None, "unit": "g"},
                    {"id": 1084, "name": "Insoluble Fiber", "amount": None, "unit": "g"},
                    {"id": 1063, "name": "Total Sugars", "amount": None, "unit": "g"},
                    {"id": 1235, "name": "Added Sugars", "amount": None, "unit": "g"},
                    {"id": 1086, "name": "Sugar Alcohol", "amount": None, "unit": "g"},
                    {"id": 1003, "name": "Protein", "amount": None, "unit": "g"},
                    {"id": 1114, "name": "Vitamin D", "amount": None, "unit": "mcg"},
                    {"id": 1087, "name": "Calcium", "amount": None, "unit": "mg"},
                    {"id": 1089, "name": "Iron", "amount": None, "unit": "mg"},
                    {"id": 1092, "name": "Potassium", "amount": None, "unit": "mg"},
                    {"id": 1106, "name": "Vitamin A", "amount": None, "unit": "mcg"},
                    {"id": 1162, "name": "Vitamin C", "amount": None, "unit": "mg"},
                    {"id": 1109, "name": "Vitamin E", "amount": None, "unit": "mg"},
                    {"id": 1183, "name": "Vitamin K", "amount": None, "unit": "mcg"},
                    {"id": 1165, "name": "Thiamin", "amount": None, "unit": "mg"},
                    {"id": 1166, "name": "Riboflavin", "amount": None, "unit": "mg"},
                    {"id": 1167, "name": "Niacin", "amount": None, "unit": "mg"},
                    {"id": 1175, "name": "Vitamin B6", "amount": None, "unit": "mg"},
                    {"id": 1177, "name": "Folate DFE", "amount": None, "unit": "mcg"},
                    {"id": 1178, "name": "Vitamin B12", "amount": None, "unit": "mcg"},
                    {"id": 1176, "name": "Biotin", "amount": None, "unit": "mcg"},
                    {"id": 1170, "name": "Pantothenic Acid", "amount": None, "unit": "mg"},
                    {"id": 1091, "name": "Phosphorus", "amount": None, "unit": "mg"},
                    {"id": 1100, "name": "Iodine", "amount": None, "unit": "mcg"},
                    {"id": 1090, "name": "Magnesium", "amount": None, "unit": "mg"},
                    {"id": 1095, "name": "Zinc", "amount": None, "unit": "mg"},
                    {"id": 1103, "name": "Selenium", "amount": None, "unit": "mcg"},
                    {"id": 1098, "name": "Copper", "amount": None, "unit": "mg"},
                    {"id": 1101, "name": "Manganese", "amount": None, "unit": "mg"},
                    {"id": 1096, "name": "Chromium", "amount": None, "unit": "mcg"},
                    {"id": 1102, "name": "Molybdenum", "amount": None, "unit": "mcg"},
                    {"id": 1180, "name": "Choline", "amount": None, "unit": "mg"},
                ],
            },
        )

    def test_member_ingredients_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertJSONEqual(
            JSONRenderer().render(data["member_ingredients"]),
            [
                {
                    "external_id": str(self.USER_INGREDIENT_MEMBERSHIP.external_id),
                    "display_ingredient": {
                        "external_id": str(self.USER_INGREDIENT.external_id),
                        "display_name": "test",
                        "display_brand": {},
                    },
                    "display_portion": {
                        "external_id": str(self.USER_INGREDIENT_MEMBERSHIP_PORTION.external_id),
                        "name": "50g",
                        "serving_size": 50.0,
                        "serving_size_unit": "g",
                        "servings_per_container": None,
                        "quantity": 50.0,
                    },
                    "ingredient_portion_external_id": "-2",
                }
            ],
        )

    def test_member_recipes_content(self):
        data = self.SERIALIZED_USER_MEAL.data
        self.assertJSONEqual(
            JSONRenderer().render(data["member_recipes"]),
            [
                {
                    "external_id": str(self.USER_MEMBER_RECIPE_MEMBERSHIP.external_id),
                    "display_recipe": {
                        "external_id": str(self.USER_MEMBER_RECIPE.external_id),
                        "name": "Test Recipe 2",
                        "recipe_date": timezone.localdate().strftime("%Y-%m-%d"),
                    },
                    "display_portion": {
                        "external_id": str(self.USER_MEMBER_RECIPE_MEMBERSHIP_PORTION.external_id),
                        "name": "50g",
                        "serving_size": 50.0,
                        "serving_size_unit": "g",
                        "servings_per_container": None,
                        "quantity": 50.0,
                    },
                    "recipe_portion_external_id": "-2",
                }
            ],
        )
