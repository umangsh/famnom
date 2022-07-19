from __future__ import annotations

from crispy_forms.layout import Div, Layout
from crispy_forms.utils import render_crispy_form
from django import forms
from django.test import SimpleTestCase

from nutrition_tracker.forms import FormHelperBase, FormsetHelperBase, layout
from nutrition_tracker.tests import utils as test_utils


class TestForm(forms.Form):
    val1 = forms.CharField(label="Val1", required=False)
    threshold_val2 = forms.CharField(label="", required=False)


class TestFormHelper(FormHelperBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_class = "col-lg-3"
        self.field_class = "col-lg-6 threshold-value"


TestFormset = forms.formset_factory(TestForm, extra=1, can_delete=True)


class TestFormsetHelper(FormsetHelperBase):
    def __init__(self, formset, *args, **kwargs):
        super().__init__(formset, *args, **kwargs)
        self.layout = Layout(Div("val1"), Div("threshold_val2"), Div("DELETE"))


class TestFormsLayoutThresholdDiv(SimpleTestCase):
    maxDiff = None

    def test_valid_html(self):
        test_form = TestForm()
        test_form.helper = TestFormHelper()
        test_form.helper.layout = Layout(layout.ThresholdDiv("val1", "threshold_val2"))

        with open("%s/test_form_layout_threshold_div_valid_html.txt" % test_utils.get_golden_dir()) as golden:
            self.assertHTMLEqual(golden.read(), render_crispy_form(test_form))


class TestFormsFormset(SimpleTestCase):
    maxDiff = None

    def test_valid_html(self):
        formset = TestFormset(prefix="test")
        formset_helper = TestFormsetHelper(formset)

        with open("%s/test_form_layout_formset_valid_html.txt" % test_utils.get_golden_dir()) as golden:
            self.assertHTMLEqual(golden.read(), render_crispy_form(formset, helper=formset_helper))
