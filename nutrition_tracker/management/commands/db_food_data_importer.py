"""
1. Import User and USDA foods in DB Base foods.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}

2. Creates the appropriate DB data. Data is never deleted - only appended or updated.

3. No data is changed in dry run.
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.models import (
    db_branded_food,
    db_food,
    db_food_nutrient,
    db_food_portion,
    usda_branded_food,
    usda_food,
    usda_food_nutrient,
    usda_foundation_food,
)

STATUS_UPDATE_BATCH_SIZE = 1000


class Command(BaseCommand):
    """Import USDA tables to DB Food (base) tables"""

    help = "Import USDA tables to DB Food (base) tables"

    def add_arguments(self, parser: CommandParser) -> None:
        """Command arguments."""
        parser.add_argument(
            "--stypes",
            type=int,
            nargs="*",
            help="source_types",
            choices=[s.value for s in constants.DBFoodSourceType if s != constants.DBFoodSourceType.UNKNOWN],
        )
        parser.add_argument(
            "--subtypes",
            type=int,
            nargs="*",
            help="source_sub_types",
            choices=[
                s.value
                for s in constants.DBFoodSourceSubType
                if s not in [constants.DBFoodSourceSubType.UNKNOWN, constants.DBFoodSourceSubType.OTHER]
            ],
        )
        parser.add_argument("--start", type=int, default=0, help="start")
        parser.add_argument("--rows", type=int, default=0, help="rows")
        parser.add_argument("--dry_run", action="store_true", help="dry run")

    def handle(self, *args: Any, **options: Any) -> None:
        """Run command."""
        source_types: list[int] = options["stypes"]
        source_sub_types: list[int] = options["subtypes"]
        dry_run: bool = options["dry_run"]
        start: int = options["start"]
        rows: int = options["rows"]

        self.process_source_types(source_types, source_sub_types, dry_run, start, rows)

    def process_source_types(  # pylint: disable=too-many-arguments
        self, source_types: list[int], source_sub_types: list[int], dry_run: bool, start: int, rows: int
    ) -> None:
        """Process source types."""
        if source_types is None:
            source_types = [s.value for s in constants.DBFoodSourceType if s != constants.DBFoodSourceType.UNKNOWN]

        for source_type in source_types:
            if source_type == constants.DBFoodSourceType.USDA:
                self.process_usda_foods(source_sub_types, dry_run, start, rows)
            elif source_type == constants.DBFoodSourceType.USER:
                self.process_user_foods()
            self.stdout.write("=" * 80)

    def process_user_foods(self) -> None:
        """Process User foods."""
        self.stdout.write("Processing User Foods")
        self.stdout.write("-" * 80)

        # Don't have a clear import story. How to differentiate
        # between edits on self-created objects and edits on foods
        # created by others. Should we care?
        processed_count: int = 0
        skipped_count: int = 0

        self.stdout.write(f"Processed {processed_count} foods ...")
        self.stdout.write(f"Skipped {skipped_count} foods ...")

    def process_usda_foods(self, source_sub_types: list[int], dry_run: bool, start: int, rows: int) -> None:
        """Process USDA Foods."""
        self.stdout.write("Processing USDA Foods")
        self.stdout.write("-" * 80)

        data_types: list[str] = constants.USDA_DATA_TYPES
        if source_sub_types is not None:
            data_types = [
                constants.DB_SUB_TYPE_TO_USDA_TYPE_MAP[constants.DBFoodSourceSubType(t)] for t in source_sub_types
            ]

        processed_count: int = 0
        skipped_count: int = 0
        for cfood_usda in usda_food.load_cfoods_iterator(start=start, rows=rows, data_types=data_types):
            processed_count += 1
            if processed_count % STATUS_UPDATE_BATCH_SIZE == 0:
                self.stdout.write(f"Processed {processed_count} foods ...")
                self.stdout.write(f"Skipped {skipped_count} foods ...")

            if not should_import_usda_food(cfood_usda):
                skipped_count += 1
                continue

            import_usda_food(cfood_usda, dry_run)

        self.stdout.write(f"Processed {processed_count} foods ...")
        self.stdout.write(f"Skipped {skipped_count} foods ...")


def import_usda_food(cfood_usda: usda_food.USDAFood, dry_run: bool) -> None:
    """Import USDA Foods."""
    if not dry_run:
        with transaction.atomic():
            db_food.update_or_create(
                source_id=cfood_usda.fdc_id,
                source_type=constants.DBFoodSourceType.USDA,
                defaults={
                    "source_sub_type": constants.USDA_TYPE_TO_DB_SUB_TYPE_MAP[cfood_usda.data_type]
                    if cfood_usda.data_type
                    else constants.DBFoodSourceSubType.UNKNOWN,
                    "description": cfood_usda.description,
                    "food_category_id": cfood_usda.food_category_id,
                },
            )

            cfood_db: db_food.DBFood | None = db_food.load_cfood(
                source_id=cfood_usda.fdc_id, source_type=constants.DBFoodSourceType.USDA
            )
            if hasattr(cfood_usda, "usdabrandedfood") and cfood_usda.usdabrandedfood:
                db_branded_food.update_or_create(
                    db_food=cfood_db,
                    defaults={
                        "brand_owner": cfood_usda.usdabrandedfood.brand_owner,
                        "brand_name": cfood_usda.usdabrandedfood.brand_name,
                        "subbrand_name": cfood_usda.usdabrandedfood.subbrand_name,
                        "gtin_upc": cfood_usda.usdabrandedfood.gtin_upc,
                        "ingredients": cfood_usda.usdabrandedfood.ingredients,
                        "not_a_significant_source_of": cfood_usda.usdabrandedfood.not_a_significant_source_of,
                    },
                )

            for cfood_nutrient in cfood_usda.usdafoodnutrient_set.all():
                db_food_nutrient.update_or_create(
                    source_id=cfood_nutrient.id,
                    source_type=constants.DBFoodSourceType.USDA,
                    defaults={
                        "db_food": cfood_db,
                        "nutrient_id": cfood_nutrient.nutrient_id,
                        "amount": cfood_nutrient.amount,
                    },
                )

            for cfood_portion in cfood_usda.usdafoodportion_set.all():
                db_food_portion.update_or_create(
                    db_food=cfood_db,
                    source_id=cfood_portion.id,
                    source_type=constants.DBFoodSourceType.USDA,
                    defaults={
                        "serving_size": cfood_portion.gram_weight,
                        "serving_size_unit": constants.ServingSizeUnit.WEIGHT,
                        "amount": cfood_portion.amount,
                        "measure_unit_id": cfood_portion.measure_unit_id,
                        "portion_description": cfood_portion.portion_description,
                        "modifier": cfood_portion.modifier,
                    },
                )

            if (
                hasattr(cfood_usda, "usdabrandedfood")
                and cfood_usda.usdabrandedfood
                and cfood_usda.usdabrandedfood.serving_size
            ):
                serving_size_unit = constants.ServingSizeUnit.WEIGHT
                if cfood_usda.usdabrandedfood.serving_size_unit:
                    serving_size_unit = constants.ServingSizeUnit(cfood_usda.usdabrandedfood.serving_size_unit.lower())
                db_food_portion.update_or_create(
                    db_food=cfood_db,
                    source_id=constants.BRANDED_FOOD_PORTION_ID,
                    source_type=constants.DBFoodSourceType.USDA,
                    defaults={
                        "serving_size": cfood_usda.usdabrandedfood.serving_size,
                        "serving_size_unit": serving_size_unit,
                        "portion_description": cfood_usda.usdabrandedfood.household_serving_fulltext,
                    },
                )


def should_import_usda_food(cfood_usda: usda_food.USDAFood) -> bool:
    """Should import USDA Food."""
    if (
        food_nutrient.get_nutrient_amount(list(cfood_usda.usdafoodnutrient_set.all()), constants.ENERGY_NUTRIENT_ID)
        is None
    ):
        return False

    if cfood_usda.data_type == constants.USDA_FOUNDATION_FOOD:
        return should_import_usda_foundation_food(cfood_usda)

    if cfood_usda.data_type == constants.USDA_SR_LEGACY_FOOD:
        return should_import_usda_sr_legacy_food(cfood_usda)

    if cfood_usda.data_type == constants.USDA_SURVEY_FNDDS_FOOD:
        return should_import_usda_survey_fndds_food(cfood_usda)
    if cfood_usda.data_type == constants.USDA_BRANDED_FOOD:
        return should_import_usda_branded_food(cfood_usda)

    # Unexpected. Don't index foods if we are here.
    return False


def should_import_usda_foundation_food(cfood_usda: usda_food.USDAFood) -> bool:
    """Should import USDA Foundation Food."""
    qs: QuerySet[usda_food.USDAFood] = usda_food.load_cfoods(
        description=cfood_usda.description, data_types=[constants.USDA_FOUNDATION_FOOD]
    )
    if qs.count() > 1:
        # If multiple foundation foods exist with the same name,
        # import the food with latest publication_date.
        # If all publication_dates are null, then return the food with the most nutrients.
        values = [
            (
                cf.publication_date if cf.publication_date else timezone.datetime.min.date(),
                usda_food_nutrient.load_nutrients(fdc_ids=[cf.fdc_id]).count(),
                cf.fdc_id,
            )
            for cf in qs
        ]
        sorted_values = sorted(values, key=lambda x: (x[0], x[1]), reverse=True)
        if cfood_usda.fdc_id != sorted_values[0][2]:
            return False

    return True


def should_import_usda_sr_legacy_food(cfood_usda: usda_food.USDAFood) -> bool:
    """Should import USDA SR Legacy Food."""
    qs: QuerySet[usda_food.USDAFood] = usda_food.load_cfoods(
        description=cfood_usda.description, data_types=[constants.USDA_FOUNDATION_FOOD]
    )
    if qs.count() > 0:
        # Don't import sr legacy food if another foundation food
        # exists with the same name.
        return False

    qs_ff: QuerySet[usda_foundation_food.USDAFoundationFood] = usda_foundation_food.load_foundation_foods(
        ndb_number=cfood_usda.usdasrlegacy.ndb_number
    )
    if qs_ff.count() > 0:
        # Don't import sr legacy food if another foundation
        # food exists with the same ndb_number.
        return False

    return True


def should_import_usda_survey_fndds_food(cfood_usda: usda_food.USDAFood) -> bool:
    """Should import USDA Survey FNDDS Food."""
    qs: QuerySet[usda_food.USDAFood] = usda_food.load_cfoods(
        description=cfood_usda.description, data_types=[constants.USDA_FOUNDATION_FOOD, constants.USDA_SR_LEGACY_FOOD]
    )
    if qs.count() > 0:
        # Don't import survey fndds food if another foundation food
        # or sr legacy food exists with the same name.
        return False

    return True


def should_import_usda_branded_food(cfood_usda: usda_food.USDAFood) -> bool:
    """Should import USDA Branded Food."""
    qs: QuerySet[usda_food.USDAFood] = usda_food.load_cfoods(
        description=cfood_usda.description,
        data_types=[constants.USDA_FOUNDATION_FOOD, constants.USDA_SR_LEGACY_FOOD, constants.USDA_SURVEY_FNDDS_FOOD],
    )
    if qs.count() > 0:
        # Don't import branded food if another foundation food
        # or sr legacy food or survey fndds food exists with the same name.
        return False

    if cfood_usda.usdabrandedfood.gtin_upc:
        qs_bf: QuerySet[usda_branded_food.USDABrandedFood] = usda_branded_food.load_cbranded_foods(
            gtin_upc=cfood_usda.usdabrandedfood.gtin_upc
        )
        if qs_bf.count() > 1:
            # If multiple branded foods exist with the same UPC,
            # import the food with latest available_date.
            # If all available_dates are null, then return the food with the most nutrients.
            values = [
                (
                    cbf.available_date if cbf.available_date else timezone.datetime.min.date(),
                    usda_food_nutrient.load_nutrients(fdc_ids=[cbf.usda_food_id]).count(),
                    cbf.usda_food_id,
                )
                for cbf in qs_bf
            ]
            sorted_values = sorted(values, key=lambda x: (x[0], x[1]), reverse=True)
            if cfood_usda.fdc_id != sorted_values[0][2]:
                return False

    return True
