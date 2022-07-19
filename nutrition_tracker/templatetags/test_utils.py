from __future__ import annotations

from django.template import Context, Template
from django.test import TestCase
from django.test.client import RequestFactory

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.templatetags import utils
from nutrition_tracker.tests import objects as test_objects


class TestTemplateTagsUtils(TestCase):
    def test_highlight_base(self):
        path = "/my_dummy_page/ABC/DEF/"
        paths = (
            "my_dummy_page",
            "other_page",
        )
        self.assertTrue(utils._highlight_base(path, paths))
        paths = ("other_page",)
        self.assertFalse(utils._highlight_base(path, paths))

    def test_get_lfood_cfood_from_context(self):
        lfood = test_objects.get_user_ingredient()
        context = Context({"lfoods": [lfood], "cfoods": [lfood.db_food]})
        return_lfood, return_cfood = utils._get_lfood_cfood_from_context(context, lfood_id=lfood.id)
        self.assertEqual(vars(lfood), vars(return_lfood))
        self.assertEqual(vars(lfood.db_food), vars(return_cfood))

        context = Context({"lfood": lfood, "cfood": lfood.db_food})
        return_lfood, return_cfood = utils._get_lfood_cfood_from_context(context)
        self.assertEqual(vars(lfood), vars(return_lfood))
        self.assertEqual(vars(lfood.db_food), vars(return_cfood))

    def test_get_lrecipe_from_context(self):
        lrecipe = test_objects.get_recipe()
        context = Context({"lrecipe": lrecipe})
        return_lrecipe = utils._get_lrecipe_from_context(context)
        self.assertEqual(vars(lrecipe), vars(return_lrecipe))

        context = Context({"lrecipes": [lrecipe]})
        return_lrecipe = utils._get_lrecipe_from_context(context, lrecipe_id=lrecipe.id)
        self.assertEqual(vars(lrecipe), vars(return_lrecipe))

        context = Context({"member_recipes": [lrecipe]})
        return_lrecipe = utils._get_lrecipe_from_context(context, lrecipe_id=lrecipe.id)
        self.assertEqual(vars(lrecipe), vars(return_lrecipe))

    def test_get_item(self):
        out = Template("{% load utils %}" "{{ dictionary|get_item:key }}").render(
            Context(
                {
                    "dictionary": {
                        1: "one",
                        2: "two",
                    },
                    "key": 2,
                }
            )
        )
        self.assertEqual(out, "two")

    def test_get_classname(self):
        lfood = test_objects.get_user_ingredient()
        out = Template("{% load utils %}" "{{ lfood|get_classname }}").render(Context({"lfood": lfood}))
        self.assertEqual(out, "UserIngredient")

    def test_get_content_type_ingredient_id(self):
        out = Template("{% load utils %}" "{% get_content_type_ingredient_id as c %}" "{{ c }}").render(Context({}))
        self.assertEqual(data_loaders.get_content_type_ingredient_id(), int(out))

    def test_get_content_type_recipe_id(self):
        out = Template("{% load utils %}" "{% get_content_type_recipe_id as c %}" "{{ c }}").render(Context({}))
        self.assertEqual(data_loaders.get_content_type_recipe_id(), int(out))

    def test_get_content_type_meal_id(self):
        out = Template("{% load utils %}" "{% get_content_type_meal_id as c %}" "{{ c }}").render(Context({}))
        self.assertEqual(data_loaders.get_content_type_meal_id(), int(out))

    def test_normalize_portion_size(self):
        context = Context()
        self.assertEqual(0, utils.normalize_portion_size(context, 0))

        out = Template("{% load utils %}" "{% normalize_portion_size value as amount %}" "{{ amount }}").render(
            Context(
                {
                    "value": 50,
                    "default_portion": (1, 2, 50),
                    "default_portion_quantity": 3,
                }
            )
        )
        self.assertEqual("75.0", out)

    def test_display_nutrient_name(self):
        out = Template("{% load utils %}" "{{ nutrient_id|display_nutrient_name }}").render(
            Context({"nutrient_id": constants.ENERGY_NUTRIENT_ID})
        )
        self.assertEqual("Calories", out)

    def test_display_nutrient_unit(self):
        out = Template("{% load utils %}" "{{ nutrient_id|display_nutrient_unit }}").render(
            Context({"nutrient_id": constants.ENERGY_NUTRIENT_ID})
        )
        self.assertEqual("kcal", out)

    def test_display_portion(self):
        out = Template("{% load utils %}" "{{ portion|display_portion }}").render(
            Context({"portion": test_objects.get_user_food_portion()})
        )
        self.assertEqual("83g", out)

    def test_display_food_name(self):
        lfood = test_objects.get_user_ingredient()
        out = Template("{% load utils %}" "{% display_food_name as name %}" "{{ name }}").render(
            Context({"lfood": lfood})
        )
        self.assertEqual("test", out)

        out = Template("{% load utils %}" "{% display_food_name as name %}" "{{ name }}").render(
            Context({"cfood": lfood.db_food})
        )
        self.assertEqual("test", out)

    def test_display_brand_field(self):
        lfood = test_objects.get_user_ingredient()
        lfood.branded_foods = [test_objects.get_user_branded_food()]
        out = Template("{% load utils %}" "{% display_brand_field fieldname as name %}" "{{ name }}").render(
            Context(
                {
                    "lfood": lfood,
                    "fieldname": "brand_name",
                }
            )
        )
        self.assertEqual("brand", out)

        test_objects.get_db_branded_food()
        lfood.db_food.refresh_from_db()
        out = Template("{% load utils %}" "{% display_brand_field fieldname as name %}" "{{ name }}").render(
            Context(
                {
                    "cfood": lfood.db_food,
                    "fieldname": "brand_name",
                }
            )
        )
        self.assertEqual("brand", out)

    def test_display_category_name(self):
        out = Template("{% load utils %}" "{{ category_id|display_category_name }}").render(
            Context(
                {
                    "category_id": 1,
                }
            )
        )
        self.assertEqual("Dairy and Egg Products", out)

    def test_display_brand_details(self):
        lfood = test_objects.get_user_ingredient()
        lfood.branded_foods = [test_objects.get_user_branded_food()]
        out = Template("{% load utils %}" "{% display_brand_details as name %}" "{{ name }}").render(
            Context(
                {
                    "lfood": lfood,
                }
            )
        )
        self.assertEqual("brand, owner", out)

        test_objects.get_db_branded_food()
        lfood.db_food.refresh_from_db()
        out = Template("{% load utils %}" "{% display_brand_details as name %}" "{{ name }}").render(
            Context(
                {
                    "cfood": lfood.db_food,
                }
            )
        )
        self.assertEqual("brand, owner", out)

    def test_display_recipe_name(self):
        lrecipe = test_objects.get_recipe()
        out = Template("{% load utils %}" "{% display_recipe_name as name %}" "{{ name }}").render(
            Context(
                {
                    "lrecipe": lrecipe,
                }
            )
        )
        self.assertEqual("Test Recipe: Today", out)

    def test_display_recipe_date(self):
        lrecipe = test_objects.get_recipe()
        out = Template("{% load utils %}" "{% display_recipe_date as name %}" "{{ name }}").render(
            Context(
                {
                    "lrecipe": lrecipe,
                }
            )
        )
        self.assertEqual("Today", out)

    def test_get_threshold_value(self):
        luser_preference = test_objects.get_user_preference()
        out = Template("{% load utils %}" "{% get_threshold_value lp as value %}" "{{ value }}").render(
            Context(
                {
                    "lp": luser_preference,
                }
            )
        )
        self.assertEqual("5.0", out)

    def test_get_nutrient_amount(self):
        lfood_nutrient = test_objects.get_user_food_nutrient()
        lfood = lfood_nutrient.ingredient
        out = Template("{% load utils %}" "{% get_nutrient_amount nutrient_id as value %}" "{{ value }}").render(
            Context(
                {
                    "food_nutrients": [lfood_nutrient],
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                }
            )
        )
        self.assertEqual("100", out)

        out = Template("{% load utils %}" "{% get_nutrient_amount nutrient_id type as value %}" "{{ value }}").render(
            Context(
                {
                    "food_nutrients": [lfood_nutrient],
                    "lfood": lfood,
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                    "type": constants.FOOD_NUTRIENTS,
                }
            )
        )
        self.assertEqual("100", out)

        out = Template("{% load utils %}" "{% get_nutrient_amount nutrient_id type as value %}" "{{ value }}").render(
            Context(
                {
                    "food_nutrients": [lfood_nutrient],
                    "lfoods": [lfood],
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                    "type": constants.FOODS_NUTRIENTS,
                }
            )
        )
        self.assertEqual("100", out)

        lrecipe = test_objects.get_recipe()
        lrecipe.portions = [test_objects.get_user_recipe_portion()]
        ufm = test_objects.get_user_food_membership(lrecipe, lfood)
        ufm.portions = [test_objects.get_user_food_membership_portion(ufm)]
        lrecipe.members = [ufm]
        out = Template("{% load utils %}" "{% get_nutrient_amount nutrient_id type as value %}" "{{ value }}").render(
            Context(
                {
                    "food_nutrients": [lfood_nutrient],
                    "lrecipe": lrecipe,
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                    "type": constants.RECIPE_NUTRIENTS,
                }
            )
        )
        self.assertEqual("25.0", out)

    def test_get_rdi_amount(self):
        luser_preference = test_objects.get_nutrient_preference()
        out = Template("{% load utils %}" "{% get_rdi_amount nutrient_id as value %}" "{{ value }}").render(
            Context(
                {
                    "nutrient_preferences": [luser_preference],
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                }
            )
        )
        self.assertEqual("1000.0", out)

        out = Template("{% load utils %}" "{% get_rdi_amount nutrient_id as value %}" "{{ value }}").render(
            Context(
                {
                    "nutrient_id": constants.ENERGY_NUTRIENT_ID,
                }
            )
        )
        self.assertEqual("2000", out)

    def test_highlight_index(self):
        path = ""
        self.assertTrue(utils.highlight_index(path))
        path = "abcd"
        self.assertFalse(utils.highlight_index(path))

    def test_highlight_search(self):
        path = "search"
        self.assertTrue(utils.highlight_search(path))
        path = "abcd"
        self.assertFalse(utils.highlight_search(path))

    def test_highlight_mealplan(self):
        path = "my_mealplan"
        self.assertTrue(utils.highlight_mealplan(path))
        path = "abcd"
        self.assertFalse(utils.highlight_mealplan(path))

    def test_highlight_kitchen(self):
        path = "my_foods"
        self.assertTrue(utils.highlight_kitchen(path))
        path = "abcd"
        self.assertFalse(utils.highlight_kitchen(path))

    def test_highlight_foods(self):
        path = "my_foods"
        self.assertTrue(utils.highlight_foods(path))
        path = "abcd"
        self.assertFalse(utils.highlight_foods(path))

    def test_highlight_recipes(self):
        path = "my_recipes"
        self.assertTrue(utils.highlight_recipes(path))
        path = "abcd"
        self.assertFalse(utils.highlight_recipes(path))

    def test_highlight_meals(self):
        path = "my_meals"
        self.assertTrue(utils.highlight_meals(path))
        path = "abcd"
        self.assertFalse(utils.highlight_meals(path))

    def test_url_replace(self):
        out = Template("{% load utils %}" "{% url_replace page=2 abcd=3 %}").render(
            Context(
                {
                    "request": RequestFactory().get("/?page=1"),
                }
            )
        )
        self.assertEqual("page=2&amp;abcd=3", out)
