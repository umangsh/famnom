from __future__ import annotations

from django.test import RequestFactory, TestCase
from rest_framework.renderers import JSONRenderer

from nutrition_tracker.models import user_ingredient
from nutrition_tracker.rest_framework.views import APIDetailsUserIngredient
from nutrition_tracker.serializers import UserIngredientDisplaySerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserIngredientDisplay(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        request = RequestFactory().get("/")
        request.user = cls.USER

        cls.USER_FOOD = test_objects.get_user_ingredient()
        cls.USER_FOOD_PORTION = test_objects.get_user_food_portion()
        test_objects.get_user_branded_food()
        test_objects.get_user_food_nutrient()
        cls.USER_FOOD = user_ingredient.load_lfood(cls.USER, external_id=cls.USER_FOOD.external_id)

        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, cls.USER_FOOD)
        test_objects.get_user_food_membership_portion(ufm)
        cls.USER_INGREDIENT_MEMBERSHIP = ufm

        view = APIDetailsUserIngredient.as_view()
        view.kwargs = {"id": cls.USER_FOOD.external_id, "mid": cls.USER_INGREDIENT_MEMBERSHIP.external_id}

        cls.SERIALIZED_USER_FOOD = UserIngredientDisplaySerializer(
            instance=cls.USER_FOOD, context={"request": request, "view": view}
        )

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(
            set(data.keys()),
            {
                "external_id",
                "display_name",
                "display_brand",
                "display_portions",
                "display_nutrients",
                "display_membership",
                "display_category",
            },
        )

    def test_external_id_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["external_id"], str(self.USER_FOOD.external_id))

    def test_display_name_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["display_name"], self.USER_FOOD.display_name)

    def test_brand_name_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["display_brand"]["brand_name"], self.USER_FOOD.display_brand_field("brand_name"))

    def test_brand_owner_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["display_brand"]["brand_owner"], self.USER_FOOD.display_brand_field("brand_owner"))

    def test_gtin_upc_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["display_brand"]["gtin_upc"], self.USER_FOOD.display_brand_field("gtin_upc"))

    def test_display_portions_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertJSONEqual(
            JSONRenderer().render(data["display_portions"]),
            [
                {
                    "external_id": str(self.USER_FOOD_PORTION.external_id),
                    "name": "83g",
                    "serving_size": 83.0,
                    "serving_size_unit": "g",
                    "servings_per_container": None,
                    "quantity": None,
                },
                {
                    "external_id": "-1",
                    "name": "100g",
                    "serving_size": 100,
                    "serving_size_unit": "g",
                    "servings_per_container": None,
                    "quantity": None,
                },
                {
                    "external_id": "-2",
                    "name": "1g",
                    "serving_size": 1,
                    "serving_size_unit": "g",
                    "servings_per_container": None,
                    "quantity": None,
                },
                {
                    "external_id": "-3",
                    "name": "1oz",
                    "serving_size": 28.3495,
                    "serving_size_unit": "g",
                    "servings_per_container": None,
                    "quantity": None,
                },
            ],
        )

    def test_nutrients_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertJSONEqual(
            JSONRenderer().render(data["display_nutrients"]),
            {
                "serving_size": 100,
                "serving_size_unit": "g",
                "values": [
                    {"id": 1008, "name": "Calories", "amount": 100.0, "unit": "kcal"},
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

    def test_display_membership_content(self):
        data = self.SERIALIZED_USER_FOOD.data
        self.assertEqual(data["display_membership"]["external_id"], str(self.USER_INGREDIENT_MEMBERSHIP.external_id))
