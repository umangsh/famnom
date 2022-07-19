"""Search indexing module."""
from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.models import db_branded_food, db_food, search_result, usda_food


def should_index_usda_foundation_food(cfood: db_food.DBFood) -> bool:
    """Should index USDA Foundation Food."""
    qs: QuerySet[db_food.DBFood] = db_food.load_cfoods(
        description=cfood.description,
        source_type=constants.DBFoodSourceType.USDA,
        source_sub_type=constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD,
    )
    if qs.count() > 1:
        # If multiple foundation foods exist with the same name,
        # index the food with newest publication_date.
        # The old food is still available in db foods linked from old meals, but not visible in search anymore.
        cfoods_usda = [usda_food.load_cfood(fdc_id=cf.source_id) for cf in qs]
        cfoods_usda_null_filtered = [cf for cf in cfoods_usda if cf]
        values = [
            (cf.publication_date if cf.publication_date else timezone.datetime.min.date(), cf.fdc_id)
            for cf in cfoods_usda_null_filtered
        ]

        sorted_values = sorted(values, key=lambda x: x[0], reverse=True)
        if cfood.source_id != sorted_values[0][1]:
            return False

    return True


def should_index_usda_branded_food(cfood: db_food.DBFood) -> bool:
    """Should index USDA Branded Food."""
    if cfood.dbbrandedfood.gtin_upc:
        qs_bf: QuerySet[db_branded_food.DBBrandedFood] = db_branded_food.load_cbranded_foods(
            gtin_upc=cfood.dbbrandedfood.gtin_upc
        )
        if qs_bf.count() > 1:
            # If multiple branded foods exist with the same UPC,
            # import the food with latest available_date.
            cfoods_usda = [usda_food.load_cfood(fdc_id=cbf.db_food.source_id) for cbf in qs_bf]
            cfoods_usda_null_filtered = [cf for cf in cfoods_usda if cf]
            values = [
                (
                    cf.usdabrandedfood.available_date
                    if cf.usdabrandedfood and cf.usdabrandedfood.available_date
                    else timezone.datetime.min.date(),
                    cf.fdc_id,
                )
                for cf in cfoods_usda_null_filtered
            ]

            sorted_values = sorted(values, key=lambda x: x[0], reverse=True)
            if cfood.source_id != sorted_values[0][1]:
                return False

    return True


def should_index_food(cfood: db_food.DBFood) -> bool:
    """Should index Food."""
    if (
        cfood.source_type == constants.DBFoodSourceType.USDA
        and cfood.source_sub_type == constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD
    ):
        return should_index_usda_foundation_food(cfood)

    if (
        cfood.source_type == constants.DBFoodSourceType.USDA
        and cfood.source_sub_type == constants.DBFoodSourceSubType.USDA_BRANDED_FOOD
    ):
        return should_index_usda_branded_food(cfood)

    return True


def convert_to_search_result(cfood: db_food.DBFood) -> search_result.SearchResult:
    """Convert a DBFood object to a search result object."""
    s_result: search_result.SearchResult = search_result.SearchResult(
        external_id=cfood.external_id,
        name=cfood.description,
        source_type=cfood.source_type,
        source_sub_type=cfood.source_sub_type,
        category_id=cfood.food_category_id,
    )

    if hasattr(cfood, "dbbrandedfood") and cfood.dbbrandedfood:
        s_result.brand_owner = cfood.dbbrandedfood.brand_owner
        s_result.brand_name = cfood.dbbrandedfood.brand_name
        s_result.subbrand_name = cfood.dbbrandedfood.subbrand_name
        s_result.gtin_upc = cfood.dbbrandedfood.gtin_upc

    return s_result


def write_search_result(item: search_result.SearchResult) -> None:
    """Index search result object in search."""
    item.save()
    # Materialize search_vector on the object for faster queries.
    # SeachVectorField can be added only as an update, and not with create.
    search_result.SearchResult.objects.filter(external_id=item.external_id).update(
        search_vector=search_result.get_search_vector()
    )


def write_search_results_bulk(items: list[search_result.SearchResult], write_batch_size: int) -> None:
    """Index search result objects in search."""
    search_result.bulk_create(items, batch_size=write_batch_size)
    # Materialize search_vector on the object for faster queries.
    # SeachVectorField can be added only as an update, and not with create.
    search_result.update_search_vector()
