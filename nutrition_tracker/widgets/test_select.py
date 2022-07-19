from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.widgets import SelectWithOptionAttrs


class TestWidgetsSelectWithOptionAttrs(SimpleTestCase):
    def test_create_option(self):
        widget = SelectWithOptionAttrs(
            choices=[
                ("id1", {"label": "label1", "data-attr": "attr1"}),
                ("id2", {"label": "label2", "data-attr": "attr2"}),
            ]
        )
        expected_output = """<select name="abc">
        <option value="id1" data-attr="attr1">label1</option>
        <option value="id2" data-attr="attr2">label2</option>
        </select>"""
        self.assertHTMLEqual(expected_output, widget.render("abc", 0))
