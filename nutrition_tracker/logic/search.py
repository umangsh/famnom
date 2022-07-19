"""Search module."""
from __future__ import annotations

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.db.models import Case, Q, QuerySet, When

from nutrition_tracker.constants import constants
from nutrition_tracker.models import search_result


def search(query: str | None, raw: bool = False) -> QuerySet[search_result.SearchResult]:
    """Search query over foods index."""
    if not query:
        return search_result.empty_qs()

    # tsquery lookups will fail with space appears in the query.
    # Use websearch in that case, even if raw mode is selected.
    should_use_raw: bool = " " not in query
    if raw and should_use_raw:
        # Raw tsquery lookup instead of websearch lookups.
        # Enable prefix based lookups as well.
        query = f"{query}:*"
        search_query = SearchQuery(query, config="english", search_type="raw")
    else:
        search_query = SearchQuery(query, config="english", search_type="websearch")

    search_vectors: SearchVector = (
        SearchVector("name", config="english")
        + SearchVector("brand_name", config="english")
        + SearchVector("brand_owner", config="english")
        + SearchVector("subbrand_name", config="english")
        + SearchVector("gtin_upc", config="english")
    )
    # Raw search_type allows prefix based search.
    search_rank: SearchRank = SearchRank(search_vectors, search_query, cover_density=True)
    # Trigram similarity used for secondary ordering.
    trigram_similarity: TrigramSimilarity = TrigramSimilarity("name", query)
    qs: QuerySet[search_result.SearchResult] = (
        search_result.SearchResult.objects.filter(search_vector=search_query)
        .annotate(
            rank0=search_rank,
            # Boost foods based on types
            rank1=Case(
                When(
                    Q(source_type=constants.DBFoodSourceType.USDA)
                    & Q(source_sub_type=constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD),
                    then=16,
                ),
                When(source_type=constants.DBFoodSourceType.USER, then=8),
                When(
                    Q(source_type=constants.DBFoodSourceType.USDA)
                    & Q(source_sub_type=constants.DBFoodSourceSubType.USDA_SR_LEGACY_FOOD),
                    then=4,
                ),
                When(
                    Q(source_type=constants.DBFoodSourceType.USDA)
                    & Q(source_sub_type=constants.DBFoodSourceSubType.USDA_SURVEY_FNDDS_FOOD),
                    then=2,
                ),
                When(
                    Q(source_type=constants.DBFoodSourceType.USDA)
                    & Q(source_sub_type=constants.DBFoodSourceSubType.USDA_BRANDED_FOOD),
                    then=1,
                ),
                default=0,
            ),
            similarity=trigram_similarity,
        )
        .order_by("-rank1", "-rank0", "-similarity")
    )

    return qs


def search_barcode(barcode: str) -> QuerySet[search_result.SearchResult]:
    """Search barcode over foods index."""
    return search_result.load_results(gtin_upc=barcode)
