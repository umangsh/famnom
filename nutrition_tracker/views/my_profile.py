"""Profile page."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import ProfileForm
from nutrition_tracker.utils import exceptions


class MyProfileView(LoginRequiredMixin, FormView):
    """Profile view class."""

    form_class = ProfileForm
    template_name: str = "nutrition_tracker/my_profile.html"

    def get_success_url(self) -> str:
        messages.add_message(self.request, messages.SUCCESS, constants.MESSAGE_SUCCESS_PROFILE_SAVE)
        return reverse_lazy(constants.URL_PROFILE)

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
            }
        )
        return kwargs

    def form_valid(self, form: ProfileForm) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data()

        with transaction.atomic():
            try:
                form.save()
                if "email" in form.changed_data:
                    email = form.cleaned_data["email"]
                    messages.add_message(
                        self.request, messages.SUCCESS, _("Confirmation e-mail sent to %(email)s") % {"email": email}
                    )
            except (exceptions.UserInAnotherFamilyException, exceptions.MaxFamilySizeException) as e:
                messages.add_message(self.request, messages.ERROR, e.message)
                return self.render_to_response(context)

        return super().form_valid(form)
