from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.serializers import NutritionSerializer
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestSerializersNutrition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_nutrition_init(self):
        serializer = NutritionSerializer(
            data={
                "date_of_birth": self.USER.date_of_birth,
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_nutrition_values(self):
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)
        threshold_field_name = form_utils.get_threshold_field_name(constants.ENERGY_NUTRIENT_ID)

        serializer = NutritionSerializer(
            data={
                "date_of_birth": self.USER.date_of_birth,
                nutrient_field_name: constants.Threshold.MAX_VALUE,
                threshold_field_name: 53,
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_fda_rdi_serialization(self):
        expected_output = {
            1: {
                1106: {"value": 900, "threshold": "3", "name": "Vitamin A", "unit": "mcg"},
                1162: {"value": 90, "threshold": "3", "name": "Vitamin C", "unit": "mg"},
                1087: {"value": 1300, "threshold": "3", "name": "Calcium", "unit": "mg"},
                1089: {"value": 18, "threshold": "3", "name": "Iron", "unit": "mg"},
                1114: {"value": 20, "threshold": "3", "name": "Vitamin D", "unit": "mcg"},
                1109: {"value": 15, "threshold": "3", "name": "Vitamin E", "unit": "mg"},
                1183: {"value": 120, "threshold": "3", "name": "Vitamin K", "unit": "mcg"},
                1165: {"value": 1.2, "threshold": "3", "name": "Thiamin", "unit": "mg"},
                1166: {"value": 1.3, "threshold": "3", "name": "Riboflavin", "unit": "mg"},
                1167: {"value": 16, "threshold": "3", "name": "Niacin", "unit": "mg"},
                1175: {"value": 1.7, "threshold": "3", "name": "Vitamin B6", "unit": "mg"},
                1177: {"value": 400, "threshold": "3", "name": "Folate DFE", "unit": "mcg"},
                1178: {"value": 2.4, "threshold": "3", "name": "Vitamin B12", "unit": "mcg"},
                1176: {"value": 30, "threshold": "3", "name": "Biotin", "unit": "mcg"},
                1170: {"value": 5, "threshold": "3", "name": "Pantothenic Acid", "unit": "mg"},
                1091: {"value": 1250, "threshold": "3", "name": "Phosphorus", "unit": "mg"},
                1100: {"value": 150, "threshold": "3", "name": "Iodine", "unit": "mcg"},
                1090: {"value": 420, "threshold": "3", "name": "Magnesium", "unit": "mg"},
                1095: {"value": 11, "threshold": "3", "name": "Zinc", "unit": "mg"},
                1103: {"value": 55, "threshold": "3", "name": "Selenium", "unit": "mcg"},
                1098: {"value": 0.9, "threshold": "3", "name": "Copper", "unit": "mg"},
                1101: {"value": 2.3, "threshold": "3", "name": "Manganese", "unit": "mg"},
                1096: {"value": 35, "threshold": "3", "name": "Chromium", "unit": "mcg"},
                1102: {"value": 45, "threshold": "3", "name": "Molybdenum", "unit": "mcg"},
                1093: {"value": 2300, "threshold": "1", "name": "Sodium", "unit": "mg"},
                1092: {"value": 4700, "threshold": "3", "name": "Potassium", "unit": "mg"},
                1180: {"value": 550, "threshold": "3", "name": "Choline", "unit": "mg"},
                1004: {"value": 78, "threshold": "3", "name": "Total Fat", "unit": "g"},
                1258: {"value": 20, "threshold": "1", "name": "Saturated Fat", "unit": "g"},
                1253: {"value": 300, "threshold": "1", "name": "Cholesterol", "unit": "mg"},
                1005: {"value": 275, "threshold": "1", "name": "Total Carbohydrate", "unit": "g"},
                1003: {"value": 50, "threshold": "3", "name": "Protein", "unit": "g"},
                1008: {"value": 2000, "threshold": "1", "name": "Calories", "unit": "kcal"},
                1079: {"value": 28, "threshold": "3", "name": "Dietary Fiber", "unit": "g"},
                1235: {"value": 50, "threshold": "1", "name": "Added Sugars", "unit": "g"},
            },
            2: {
                1106: {"value": 500, "threshold": "3", "name": "Vitamin A", "unit": "mcg"},
                1162: {"value": 50, "threshold": "3", "name": "Vitamin C", "unit": "mg"},
                1087: {"value": 260, "threshold": "3", "name": "Calcium", "unit": "mg"},
                1089: {"value": 11, "threshold": "3", "name": "Iron", "unit": "mg"},
                1114: {"value": 10, "threshold": "3", "name": "Vitamin D", "unit": "mcg"},
                1109: {"value": 5, "threshold": "3", "name": "Vitamin E", "unit": "mg"},
                1183: {"value": 2.5, "threshold": "3", "name": "Vitamin K", "unit": "mcg"},
                1165: {"value": 0.3, "threshold": "3", "name": "Thiamin", "unit": "mg"},
                1166: {"value": 0.4, "threshold": "3", "name": "Riboflavin", "unit": "mg"},
                1167: {"value": 4, "threshold": "3", "name": "Niacin", "unit": "mg"},
                1175: {"value": 0.3, "threshold": "3", "name": "Vitamin B6", "unit": "mg"},
                1177: {"value": 80, "threshold": "3", "name": "Folate DFE", "unit": "mcg"},
                1178: {"value": 0.5, "threshold": "3", "name": "Vitamin B12", "unit": "mcg"},
                1176: {"value": 6, "threshold": "3", "name": "Biotin", "unit": "mcg"},
                1170: {"value": 1.8, "threshold": "3", "name": "Pantothenic Acid", "unit": "mg"},
                1091: {"value": 275, "threshold": "3", "name": "Phosphorus", "unit": "mg"},
                1100: {"value": 130, "threshold": "3", "name": "Iodine", "unit": "mcg"},
                1090: {"value": 75, "threshold": "3", "name": "Magnesium", "unit": "mg"},
                1095: {"value": 3, "threshold": "3", "name": "Zinc", "unit": "mg"},
                1103: {"value": 20, "threshold": "3", "name": "Selenium", "unit": "mcg"},
                1098: {"value": 0.2, "threshold": "3", "name": "Copper", "unit": "mg"},
                1101: {"value": 0.6, "threshold": "3", "name": "Manganese", "unit": "mg"},
                1096: {"value": 5.5, "threshold": "3", "name": "Chromium", "unit": "mcg"},
                1102: {"value": 3, "threshold": "3", "name": "Molybdenum", "unit": "mcg"},
                1093: {"value": 570, "threshold": "1", "name": "Sodium", "unit": "mg"},
                1092: {"value": 700, "threshold": "3", "name": "Potassium", "unit": "mg"},
                1180: {"value": 150, "threshold": "3", "name": "Choline", "unit": "mg"},
                1004: {"value": 30, "threshold": "3", "name": "Total Fat", "unit": "g"},
                1258: {"value": None, "threshold": "1", "name": "Saturated Fat", "unit": "g"},
                1253: {"value": None, "threshold": "1", "name": "Cholesterol", "unit": "mg"},
                1005: {"value": 95, "threshold": "1", "name": "Total Carbohydrate", "unit": "g"},
                1003: {"value": 11, "threshold": "3", "name": "Protein", "unit": "g"},
                1008: {"value": 1000, "threshold": "1", "name": "Calories", "unit": "kcal"},
                1079: {"value": None, "threshold": "3", "name": "Dietary Fiber", "unit": "g"},
                1235: {"value": None, "threshold": "1", "name": "Added Sugars", "unit": "g"},
            },
            3: {
                1106: {"value": 300, "threshold": "3", "name": "Vitamin A", "unit": "mcg"},
                1162: {"value": 15, "threshold": "3", "name": "Vitamin C", "unit": "mg"},
                1087: {"value": 700, "threshold": "3", "name": "Calcium", "unit": "mg"},
                1089: {"value": 7, "threshold": "3", "name": "Iron", "unit": "mg"},
                1114: {"value": 15, "threshold": "3", "name": "Vitamin D", "unit": "mcg"},
                1109: {"value": 6, "threshold": "3", "name": "Vitamin E", "unit": "mg"},
                1183: {"value": 30, "threshold": "3", "name": "Vitamin K", "unit": "mcg"},
                1165: {"value": 0.5, "threshold": "3", "name": "Thiamin", "unit": "mg"},
                1166: {"value": 0.5, "threshold": "3", "name": "Riboflavin", "unit": "mg"},
                1167: {"value": 6, "threshold": "3", "name": "Niacin", "unit": "mg"},
                1175: {"value": 0.5, "threshold": "3", "name": "Vitamin B6", "unit": "mg"},
                1177: {"value": 150, "threshold": "3", "name": "Folate DFE", "unit": "mcg"},
                1178: {"value": 0.9, "threshold": "3", "name": "Vitamin B12", "unit": "mcg"},
                1176: {"value": 8, "threshold": "3", "name": "Biotin", "unit": "mcg"},
                1170: {"value": 2, "threshold": "3", "name": "Pantothenic Acid", "unit": "mg"},
                1091: {"value": 460, "threshold": "3", "name": "Phosphorus", "unit": "mg"},
                1100: {"value": 90, "threshold": "3", "name": "Iodine", "unit": "mcg"},
                1090: {"value": 80, "threshold": "3", "name": "Magnesium", "unit": "mg"},
                1095: {"value": 3, "threshold": "3", "name": "Zinc", "unit": "mg"},
                1103: {"value": 20, "threshold": "3", "name": "Selenium", "unit": "mcg"},
                1098: {"value": 0.3, "threshold": "3", "name": "Copper", "unit": "mg"},
                1101: {"value": 1.2, "threshold": "3", "name": "Manganese", "unit": "mg"},
                1096: {"value": 11, "threshold": "3", "name": "Chromium", "unit": "mcg"},
                1102: {"value": 17, "threshold": "3", "name": "Molybdenum", "unit": "mcg"},
                1093: {"value": 1500, "threshold": "1", "name": "Sodium", "unit": "mg"},
                1092: {"value": 3000, "threshold": "3", "name": "Potassium", "unit": "mg"},
                1180: {"value": 200, "threshold": "3", "name": "Choline", "unit": "mg"},
                1004: {"value": 39, "threshold": "3", "name": "Total Fat", "unit": "g"},
                1258: {"value": 10, "threshold": "1", "name": "Saturated Fat", "unit": "g"},
                1253: {"value": 300, "threshold": "1", "name": "Cholesterol", "unit": "mg"},
                1005: {"value": 150, "threshold": "1", "name": "Total Carbohydrate", "unit": "g"},
                1003: {"value": 13, "threshold": "3", "name": "Protein", "unit": "g"},
                1008: {"value": 1000, "threshold": "1", "name": "Calories", "unit": "kcal"},
                1079: {"value": 14, "threshold": "3", "name": "Dietary Fiber", "unit": "g"},
                1235: {"value": 25, "threshold": "1", "name": "Added Sugars", "unit": "g"},
            },
            4: {
                1106: {"value": 1300, "threshold": "3", "name": "Vitamin A", "unit": "mcg"},
                1162: {"value": 120, "threshold": "3", "name": "Vitamin C", "unit": "mg"},
                1087: {"value": 1300, "threshold": "3", "name": "Calcium", "unit": "mg"},
                1089: {"value": 27, "threshold": "3", "name": "Iron", "unit": "mg"},
                1114: {"value": 15, "threshold": "3", "name": "Vitamin D", "unit": "mcg"},
                1109: {"value": 19, "threshold": "3", "name": "Vitamin E", "unit": "mg"},
                1183: {"value": 90, "threshold": "3", "name": "Vitamin K", "unit": "mcg"},
                1165: {"value": 1.4, "threshold": "3", "name": "Thiamin", "unit": "mg"},
                1166: {"value": 1.6, "threshold": "3", "name": "Riboflavin", "unit": "mg"},
                1167: {"value": 18, "threshold": "3", "name": "Niacin", "unit": "mg"},
                1175: {"value": 2, "threshold": "3", "name": "Vitamin B6", "unit": "mg"},
                1177: {"value": 600, "threshold": "3", "name": "Folate DFE", "unit": "mcg"},
                1178: {"value": 2.8, "threshold": "3", "name": "Vitamin B12", "unit": "mcg"},
                1176: {"value": 35, "threshold": "3", "name": "Biotin", "unit": "mcg"},
                1170: {"value": 7, "threshold": "3", "name": "Pantothenic Acid", "unit": "mg"},
                1091: {"value": 1250, "threshold": "3", "name": "Phosphorus", "unit": "mg"},
                1100: {"value": 290, "threshold": "3", "name": "Iodine", "unit": "mcg"},
                1090: {"value": 400, "threshold": "3", "name": "Magnesium", "unit": "mg"},
                1095: {"value": 13, "threshold": "3", "name": "Zinc", "unit": "mg"},
                1103: {"value": 70, "threshold": "3", "name": "Selenium", "unit": "mcg"},
                1098: {"value": 1.3, "threshold": "3", "name": "Copper", "unit": "mg"},
                1101: {"value": 2.6, "threshold": "3", "name": "Manganese", "unit": "mg"},
                1096: {"value": 45, "threshold": "3", "name": "Chromium", "unit": "mcg"},
                1102: {"value": 50, "threshold": "3", "name": "Molybdenum", "unit": "mcg"},
                1093: {"value": 2300, "threshold": "1", "name": "Sodium", "unit": "mg"},
                1092: {"value": 5100, "threshold": "3", "name": "Potassium", "unit": "mg"},
                1180: {"value": 550, "threshold": "3", "name": "Choline", "unit": "mg"},
                1004: {"value": 78, "threshold": "3", "name": "Total Fat", "unit": "g"},
                1258: {"value": 20, "threshold": "1", "name": "Saturated Fat", "unit": "g"},
                1253: {"value": 300, "threshold": "1", "name": "Cholesterol", "unit": "mg"},
                1005: {"value": 275, "threshold": "1", "name": "Total Carbohydrate", "unit": "g"},
                1003: {"value": 71, "threshold": "3", "name": "Protein", "unit": "g"},
                1008: {"value": 2000, "threshold": "1", "name": "Calories", "unit": "kcal"},
                1079: {"value": 28, "threshold": "3", "name": "Dietary Fiber", "unit": "g"},
                1235: {"value": 50, "threshold": "1", "name": "Added Sugars", "unit": "g"},
            },
        }

        self.assertDictEqual(NutritionSerializer.get_fda_rdi(), expected_output)

    def test_label_nutrient_serialization(self):
        self.assertEqual(len(NutritionSerializer.get_label_nutrients()), len(constants.LABEL_NUTRIENT_IDS))
