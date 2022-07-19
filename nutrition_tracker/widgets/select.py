"""Custom Select Widgets."""
from __future__ import annotations

from typing import Any

from django.forms.widgets import Select


class SelectWithOptionAttrs(Select):
    """
    Select With Option Attrs:
        subclass of Django's Select widget that allows attributes in options,
        like disabled='disabled', title='help text', class='some classes',
        data-foo='foo', etc.
    Pass a dict instead of a string for its label:
        choices = [ ('value_1', 'label_1'),
                    ...
                    ('value_k', {'label': 'label_k', 'foo': 'bar', ...}),
                    ... ]
    The option k will be rendered as:
        <option value='value_k' data-foo='foo' ...>label_k</option>
    """

    def create_option(  # pylint: disable=too-many-arguments
        self,
        name: str,
        value: Any,
        label: int | str,
        selected: set[str] | bool,
        index: Any,
        subindex: Any | None = None,
        attrs: dict | None = None,
    ) -> dict:
        opt_attrs: dict = {}
        if isinstance(label, dict):
            # label can be a dict. mypy type inferencing doesn't allow
            # dict as a valid type.
            opt_attrs = label.copy()
            label = opt_attrs.pop("label")

        option_dict = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        for key, val in opt_attrs.items():
            option_dict["attrs"][key] = val

        return option_dict
