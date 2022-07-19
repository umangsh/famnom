from __future__ import annotations

from crispy_forms.utils import render_crispy_form
from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import NutritionForm
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils
from nutrition_tracker.utils import form as form_utils


class TestFormsNutritionForm(TestCase):
    maxDiff = None

    def test_form_empty_init(self):
        kwargs = {"user": test_objects.get_user()}
        form = NutritionForm(**kwargs)

        with open("%s/test_form_nutrition_empty.txt" % test_utils.get_golden_dir()) as golden:
            self.assertHTMLEqual(golden.read(), render_crispy_form(form))

    def test_form_init(self):
        kwargs = {"user": test_objects.get_user()}
        form = NutritionForm(**kwargs)
        self.assertIsNotNone(form.helper)

    def test_form_save(self):
        luser = test_objects.get_user()
        kwargs = {"user": luser}
        form_data = {
            "date_of_birth": luser.date_of_birth,
            "is_pregnant": luser.is_pregnant(),
            form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
            form_utils.get_field_name(constants.FAT_NUTRIENT_ID): 23,
            form_utils.get_field_name(constants.PROTEIN_NUTRIENT_ID): 89,
        }
        form = NutritionForm(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())

        form.save()
        self.assertEqual(3, user_prefs.load_nutrition_preferences(luser).count())
