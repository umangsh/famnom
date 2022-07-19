"""Search query form module."""
from __future__ import annotations

from django import forms


class SearchForm(forms.Form):
    """Form used for search query submission."""

    q = forms.CharField(max_length=100, required=False)
    fs = forms.CharField(max_length=100, required=False)
    fn = forms.CharField(max_length=100, required=False)
