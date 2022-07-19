"""Mealplan view."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import MealplanFormOne, MealplanFormThree, MealplanFormTwo
from nutrition_tracker.logic import mealplan, user_prefs

STEP_ONE: int = 1
STEP_TWO: int = 2
STEP_THREE: int = 3


FORMS: dict[int, type[MealplanFormOne] | type[MealplanFormTwo] | type[MealplanFormThree]] = {
    STEP_ONE: MealplanFormOne,
    STEP_TWO: MealplanFormTwo,
    STEP_THREE: MealplanFormThree,
}


TEMPLATES: dict[int, str] = {
    STEP_ONE: "nutrition_tracker/my_mealplan_one.html",
    STEP_TWO: "nutrition_tracker/my_mealplan_two.html",
    STEP_THREE: "nutrition_tracker/my_mealplan_three.html",
}


NEXT_URL: dict[int, str] = {
    STEP_ONE: constants.URL_MY_MEALPLAN,
    STEP_TWO: constants.URL_MY_MEALPLAN,
    STEP_THREE: constants.URL_HOME,
}


class MyMealplanView(LoginRequiredMixin, FormView):
    """My mealplan view base class."""

    def _get_step_value(self) -> int:
        step: int | None = self.kwargs.get("step")
        step = max(min(step or STEP_ONE, STEP_THREE), STEP_ONE)
        return step

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.step = self._get_step_value()  # pylint: disable=attribute-defined-outside-init
        if self.step == STEP_THREE:
            self.lmealplan = mealplan.get_mealplan_for_user(  # pylint: disable=attribute-defined-outside-init
                self.request.user  # type: ignore
            )
        return super().get(*args, **kwargs)

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        context["nutrient_preferences"] = list(user_prefs.load_nutrition_preferences(self.request.user))  # type: ignore
        if self.step == STEP_THREE:
            context["mealplan_infeasible"] = self.lmealplan.infeasible
            context["lfoods"] = self.lmealplan.lfoods
            context["lrecipes"] = self.lmealplan.lrecipes
            context["member_recipes"] = self.lmealplan.lmember_recipes
            context["lmeals"] = self.lmealplan.lmeals_today
            context["food_nutrients"] = self.lmealplan.lfoods_nutrients
            context["quantity_map"] = self.lmealplan.quantity_map
        return context

    def get_success_url(self) -> str:
        url: str = NEXT_URL[self.step]
        if self.step == STEP_ONE:
            return reverse_lazy(url, kwargs={"step": STEP_TWO})
        if self.step == STEP_TWO:
            return reverse_lazy(url, kwargs={"step": STEP_THREE})
        if self.step == STEP_THREE:
            if self.return_value:
                messages.add_message(self.request, messages.SUCCESS, constants.MESSAGE_SUCCESS_MEALPLAN_SAVE)
            else:
                messages.add_message(self.request, messages.INFO, constants.MESSAGE_INFO_MEALPLAN_NOT_SAVED)

            return reverse_lazy(url)

        return reverse_lazy(url)

    def get_form_class(self) -> Any:
        self.step = self._get_step_value()  # pylint: disable=attribute-defined-outside-init
        return FORMS[self.step]

    def get_template_names(self) -> list[str]:
        return [TEMPLATES[self.step]]

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
                "lmealplan": getattr(self, "lmealplan", []),
            }
        )
        return kwargs

    def form_valid(self, form: Any) -> HttpResponse:
        with transaction.atomic():
            self.return_value = form.save()  # pylint: disable=attribute-defined-outside-init

        return super().form_valid(form)
