from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.serializers import FormDataSerializer


class TestSerializersFormData(SimpleTestCase):
    def test_get_category_data(self):
        expected_output = [
            {"id": "", "name": "Select Category"},
            {"id": "28", "name": "Alcoholic Beverages"},
            {"id": "24", "name": "American Indian/Alaska Native Foods"},
            {"id": "3", "name": "Baby Foods"},
            {"id": "18", "name": "Baked Products"},
            {"id": "13", "name": "Beef Products"},
            {"id": "14", "name": "Beverages"},
            {"id": "26", "name": "Branded Food Products Database"},
            {"id": "8", "name": "Breakfast Cereals"},
            {"id": "20", "name": "Cereal Grains and Pasta"},
            {"id": "1", "name": "Dairy and Egg Products"},
            {"id": "21", "name": "Fast Foods"},
            {"id": "4", "name": "Fats and Oils"},
            {"id": "15", "name": "Finfish and Shellfish Products"},
            {"id": "9", "name": "Fruits and Fruit Juices"},
            {"id": "17", "name": "Lamb, Veal, and Game Products"},
            {"id": "16", "name": "Legumes and Legume Products"},
            {"id": "22", "name": "Meals, Entrees, and Side Dishes"},
            {"id": "12", "name": "Nut and Seed Products"},
            {"id": "10", "name": "Pork Products"},
            {"id": "5", "name": "Poultry Products"},
            {"id": "27", "name": "Quality Control Materials"},
            {"id": "25", "name": "Restaurant Foods"},
            {"id": "7", "name": "Sausages and Luncheon Meats"},
            {"id": "23", "name": "Snacks"},
            {"id": "6", "name": "Soups, Sauces, and Gravies"},
            {"id": "2", "name": "Spices and Herbs"},
            {"id": "19", "name": "Sweets"},
            {"id": "11", "name": "Vegetables and Vegetable Products"},
        ]
        self.assertEqual(expected_output, FormDataSerializer.get_category_data())

    def test_get_household_quantity_data(self):
        expected_output = [
            {"id": "", "name": "Select quantity"},
            {"id": "1/8", "name": "1/8"},
            {"id": "1/6", "name": "1/6"},
            {"id": "1/5", "name": "1/5"},
            {"id": "1/4", "name": "1/4"},
            {"id": "1/3", "name": "1/3"},
            {"id": "3/8", "name": "3/8"},
            {"id": "2/5", "name": "2/5"},
            {"id": "1/2", "name": "1/2"},
            {"id": "3/5", "name": "3/5"},
            {"id": "5/8", "name": "5/8"},
            {"id": "2/3", "name": "2/3"},
            {"id": "3/4", "name": "3/4"},
            {"id": "4/5", "name": "4/5"},
            {"id": "5/6", "name": "5/6"},
            {"id": "7/8", "name": "7/8"},
            {"id": "1", "name": "1"},
            {"id": "3/2", "name": "3/2"},
            {"id": "2", "name": "2"},
            {"id": "3", "name": "3"},
            {"id": "4", "name": "4"},
            {"id": "5", "name": "5"},
            {"id": "6", "name": "6"},
            {"id": "7", "name": "7"},
            {"id": "8", "name": "8"},
            {"id": "9", "name": "9"},
            {"id": "10", "name": "10"},
            {"id": "11", "name": "11"},
            {"id": "12", "name": "12"},
            {"id": "13", "name": "13"},
            {"id": "14", "name": "14"},
            {"id": "15", "name": "15"},
            {"id": "16", "name": "16"},
            {"id": "17", "name": "17"},
            {"id": "18", "name": "18"},
            {"id": "19", "name": "19"},
            {"id": "20", "name": "20"},
        ]
        self.assertEqual(expected_output, FormDataSerializer.get_household_quantity_data())

    def test_get_household_unit_data(self):
        self.assertTrue(FormDataSerializer.get_household_unit_data())

    def test_get_serving_size_unit_data(self):
        expected_output = [{"id": "", "name": "Select unit"}, {"id": "g", "name": "g"}, {"id": "ml", "name": "ml"}]
        self.assertEqual(expected_output, FormDataSerializer.get_serving_size_unit_data())
