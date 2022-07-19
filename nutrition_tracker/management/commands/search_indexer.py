"""Search Indexer Module. Clears and re-indexes all DBFoods on every run."""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import search_indexing
from nutrition_tracker.models import db_food, search_result

STATUS_UPDATE_BATCH_SIZE = 100000


class Command(BaseCommand):
    """Index foods in search index."""

    help = "Index foods in search index."

    def add_arguments(self, parser: CommandParser) -> None:
        """Command arguments."""
        parser.add_argument("--dry_run", action="store_true", help="dry run")

    def handle(self, *args: Any, **options: Any) -> None:
        """Run command."""
        dry_run: bool = options["dry_run"]

        if not dry_run:
            self.clear_index()

        index_items: list[search_result.SearchResult] = self.get_index_items()
        if not dry_run:
            self.write_index(index_items)

    def clear_index(self) -> None:
        """Clear search index."""
        self.stdout.write("Clearing old index ...")
        search_result.delete_all()
        self.stdout.write("Index cleared.")

    def get_index_items(self) -> list[search_result.SearchResult]:
        """Iterate over DBFood table, and generate search result objects to be indexed."""
        processed_count: int = 0
        skipped_count: int = 0
        sr_foods: list[search_result.SearchResult] = []
        for cfood in db_food.load_cfoods_iterator():
            processed_count += 1
            if processed_count % STATUS_UPDATE_BATCH_SIZE == 0:
                self.stdout.write(f"Processed {processed_count} foods ...")
                self.stdout.write(f"Skipped {skipped_count} foods ...")

            if not search_indexing.should_index_food(cfood):
                skipped_count += 1
                continue

            sr_food: search_result.SearchResult = search_indexing.convert_to_search_result(cfood)
            sr_foods.append(sr_food)

        self.stdout.write(f"Processed {processed_count} foods ...")
        self.stdout.write(f"Skipped {skipped_count} foods ...")
        return sr_foods

    def write_index(self, items: list[search_result.SearchResult]) -> None:
        """Write search results to search index."""
        self.stdout.write("Writing search index ...")
        search_indexing.write_search_results_bulk(items, constants.WRITE_BATCH_SIZE)
        self.stdout.write("Index written.")
