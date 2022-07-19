from __future__ import annotations

from crispy_forms.utils import render_crispy_form
from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.forms import ProfileForm
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestFormsProfileForm(TestCase):
    maxDiff = None

    def test_form_empty_init(self):
        kwargs = {"user": test_objects.get_user()}
        form = ProfileForm(**kwargs)

        with open("%s/test_form_profile_empty.txt" % test_utils.get_golden_dir()) as golden:
            self.assertHTMLEqual(golden.read(), render_crispy_form(form))

    def test_form_init(self):
        kwargs = {"user": test_objects.get_user()}
        form = ProfileForm(**kwargs)
        self.assertIsNotNone(form.helper)

    def test_form_save(self):
        luser = test_objects.get_user()
        luser_2 = test_objects.get_user_2()
        kwargs = {"user": luser}
        form_data = {
            "date_of_birth": luser.date_of_birth,
            "is_pregnant": luser.is_pregnant(),
            "email": luser.email,
            "first_name": "Updated First Name",
            "family_email": luser_2.email,
        }
        form = ProfileForm(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())

        form.save()
        luser = user.load_luser(id_=luser.id)
        luser_2 = user.load_luser(id_=luser_2.id)
        self.assertEqual(luser.first_name, "Updated First Name")
        self.assertIsNotNone(luser.family_id)
        self.assertIsNotNone(luser_2.family_id)
        self.assertEqual(luser.family_id, luser_2.family_id)
