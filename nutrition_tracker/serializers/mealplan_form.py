"""Mealplan form(s) serializer module."""
from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from drf_braces.serializers.form_serializer import FormSerializer
from rest_framework import fields

from nutrition_tracker.forms import MealplanFormOne, MealplanFormThree, MealplanFormTwo


class MealplanFormOneSerializer(FormSerializer):
    """Mealplan form one serializer class."""

    class Meta:
        form = MealplanFormOne
        field_mapping = {
            SimpleArrayField: fields.ListField,
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> MealplanFormOne:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
                "lmealplan": self.context.get("lmealplan"),
            }
        )
        return super().get_form(data=data, **kwargs)


class MealplanFormTwoSerializer(FormSerializer):
    """Mealplan form two serializer class."""

    class Meta:
        form = MealplanFormTwo
        field_mapping = {
            forms.FloatField: fields.FloatField,
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> MealplanFormTwo:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
                "lmealplan": self.context.get("lmealplan"),
            }
        )
        return super().get_form(data=data, **kwargs)


class MealplanFormThreeSerializer(FormSerializer):
    """Mealplan form three serializer class."""

    class Meta:
        form = MealplanFormThree
        field_mapping = {
            forms.FloatField: fields.FloatField,
        }

    def get_form(self, data: dict | None = None, **kwargs: Any) -> MealplanFormThree:
        """Create an instance of configured form class. Update
        kwargs with context data."""

        kwargs.update(
            {
                "user": self.context.get("user"),
                "lmealplan": self.context.get("lmealplan"),
            }
        )
        return super().get_form(data=data, **kwargs)
