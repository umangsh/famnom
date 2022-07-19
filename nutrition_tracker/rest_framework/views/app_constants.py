"""Load all app constants for REST API."""
from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.serializers import FormDataSerializer, NutritionSerializer


class APIAppConstants(APIView):
    """App constants API. Available to authenticated users only."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        response: dict[str, Any] = {}

        # FDA RDIs.
        response.update({"fda_rdis": NutritionSerializer.get_fda_rdi()})

        # Label nutrients metadata.
        response.update({"label_nutrients": NutritionSerializer.get_label_nutrients()})

        # Category metadata.
        response.update({"categories": FormDataSerializer.get_category_data()})

        # Household quantities.
        response.update({"household_quantities": FormDataSerializer.get_household_quantity_data()})

        # Household units.
        response.update({"household_units": FormDataSerializer.get_household_unit_data()})

        # Serving size units.
        response.update({"serving_size_units": FormDataSerializer.get_serving_size_unit_data()})

        return Response(response)
