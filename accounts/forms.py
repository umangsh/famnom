"""Login and singup forms."""
from __future__ import annotations

from typing import Any

from allauth.account import forms


class LoginForm(forms.LoginForm):
    """Login form"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            if fieldname == "remember":
                continue

            field.widget.attrs.update({"class": "form-control"})


class SignupForm(forms.SignupForm):
    """Signup form"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for _fieldname, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
