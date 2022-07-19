"""Nutrition goals page."""
from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import NutritionForm
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_preference
from nutrition_tracker.serializers import NutritionSerializer


class MyNutritionView(LoginRequiredMixin, FormView):
    """Nutrition goals view class."""

    form_class = NutritionForm
    template_name: str = "nutrition_tracker/my_nutrition.html"

    def get_success_url(self) -> str:
        messages.add_message(self.request, messages.SUCCESS, constants.MESSAGE_SUCCESS_NUTRITION_SAVE)
        return reverse_lazy(constants.URL_NUTRITION)

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.nutrient_preferences: list[  # pylint: disable=attribute-defined-outside-init
            user_preference.UserPreference
        ] = list(user_prefs.load_nutrition_preferences(request.user))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
                "nutrient_preferences": self.nutrient_preferences,
            }
        )
        return kwargs

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        context["fda_nutrients"] = json.dumps(NutritionSerializer.get_fda_rdi())
        return context

    def form_valid(self, form: NutritionForm) -> HttpResponse:
        with transaction.atomic():
            form.save()

        return super().form_valid(form)
