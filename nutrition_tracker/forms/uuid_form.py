"""UUID form module."""
from __future__ import annotations

from django import forms


class UUIDForm(forms.Form):
    """Form used for UUID/member UUID validation."""

    id = forms.UUIDField()
    mid = forms.UUIDField(required=False)
    nexturl = forms.CharField(required=False)
