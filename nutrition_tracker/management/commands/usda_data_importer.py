"""
1. Finds the latest USDA data directory in the default path or remote S3 bucket.

2. Processes the subdirectory specified in input:
All_Foods, Foundation_Foods, SR_Legacy, Experimental_Foods, FNDDS_Foods, Branded_Foods, Supporting_Data.

3. Creates the appropriate DB tables and / or prints updated configs for tables stored as configuration instead of DB values. Data is never deleted - only appended or updated.

4. No data is changed in dry run.
"""
from __future__ import annotations

import csv
import os
from datetime import date, datetime
from typing import Any, Callable, TextIO

import boto3
from botocore.config import Config
from decouple import config
from django.core.management.base import BaseCommand, CommandParser

from nutrition_tracker.config import usda_config
from nutrition_tracker.models import (
    usda_branded_food,
    usda_fndds_food,
    usda_food,
    usda_food_nutrient,
    usda_food_portion,
    usda_foundation_food,
    usda_sr_legacy,
)

# Types
ALL_FOODS: str = "All_Foods"
FOUNDATION_FOODS: str = "Foundation_Foods"
SR_LEGACY: str = "SR_Legacy"
EXPERIMENTAL_FOODS: str = "Experimental_Foods"
FNDDS_FOODS: str = "FNDDS_Foods"
BRANDED_FOODS: str = "Branded_Foods"
SUPPORTING_DATA: str = "Supporting_Data"

# Filenames
CSV_FOOD: str = "food.csv"
CSV_FOUNDATION_FOOD: str = "foundation_food.csv"
CSV_SR_LEGACY: str = "sr_legacy_food.csv"
CSV_FNDDS_FOOD: str = "survey_fndds_food.csv"
CSV_BRANDED_FOOD: str = "branded_food.csv"
CSV_FOOD_NUTRIENT: str = "food_nutrient.csv"
CSV_FOOD_PORTION: str = "food_portion.csv"
CSV_FOOD_CATEGORY: str = "food_category.csv"
CSV_MEASURE_UNIT: str = "measure_unit.csv"
CSV_NUTRIENT: str = "nutrient.csv"
CSV_WWEIA_FOOD_CATEGORY: str = "wweia_food_category.csv"

USDA_TYPE_MAP: dict[int, str] = {
    0: ALL_FOODS,
    1: FOUNDATION_FOODS,
    2: SR_LEGACY,
    3: EXPERIMENTAL_FOODS,
    4: FNDDS_FOODS,
    5: BRANDED_FOODS,
    6: SUPPORTING_DATA,
}

FILE_TYPE_MAP: dict[int, str] = {
    1: CSV_FOOD,
    2: CSV_FOUNDATION_FOOD,
    3: CSV_SR_LEGACY,
    4: CSV_FNDDS_FOOD,
    5: CSV_BRANDED_FOOD,
    6: CSV_FOOD_NUTRIENT,
    7: CSV_FOOD_PORTION,
    8: CSV_FOOD_CATEGORY,
    9: CSV_MEASURE_UNIT,
    10: CSV_NUTRIENT,
    11: CSV_WWEIA_FOOD_CATEGORY,
}

CSV_TO_IMPORT: dict[int, list[str]] = {
    # CSV_FOOD has to be created first.
    0: [
        CSV_FOOD,
        CSV_FOUNDATION_FOOD,
        CSV_SR_LEGACY,
        CSV_FNDDS_FOOD,
        CSV_BRANDED_FOOD,
        CSV_FOOD_NUTRIENT,
        CSV_FOOD_PORTION,
        CSV_FOOD_CATEGORY,
        CSV_MEASURE_UNIT,
        CSV_NUTRIENT,
        CSV_WWEIA_FOOD_CATEGORY,
    ],
    1: [CSV_FOOD, CSV_FOUNDATION_FOOD, CSV_FOOD_NUTRIENT, CSV_FOOD_PORTION],
    2: [CSV_FOOD, CSV_SR_LEGACY, CSV_FOOD_NUTRIENT, CSV_FOOD_PORTION],
    3: [],
    4: [CSV_FOOD, CSV_FNDDS_FOOD, CSV_FOOD_NUTRIENT, CSV_FOOD_PORTION],
    5: [CSV_FOOD, CSV_BRANDED_FOOD, CSV_FOOD_NUTRIENT],
    6: [CSV_FOOD_CATEGORY, CSV_MEASURE_UNIT, CSV_NUTRIENT, CSV_WWEIA_FOOD_CATEGORY],
}


LOCAL_BASE_PATH: str = config("LOCAL_BASE_PATH")
BASE_PATH_SUFFIX: str = "files/ingestion/sources/usda/April_2022"
S3_BUCKET_NAME: str = "famnombucket"
S3_CONFIG: Config = Config(
    region_name="us-west-1",
    retries={
        "max_attempts": 3,
        "mode": "standard",
    },
)


def get_filepath(remote: bool, subdir: str, filename: str, write_fn: Callable) -> str:
    """Get base filepath for USDA data."""
    if remote:
        return get_remote_filepath(subdir, filename, write_fn)

    return get_local_filepath(subdir, filename)


def get_remote_filepath(subdir: str, filename: str, write_fn: Callable) -> str:
    """Get base filepath for USDA data from AWS. Downloads data from AWS."""
    object_name: str = f"{BASE_PATH_SUFFIX}/{subdir}/{filename}"
    write_fn(f"Fetching {object_name} from S3")
    write_fn("-" * 80)
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
        config=S3_CONFIG,
    )
    s3_client.download_file(S3_BUCKET_NAME, object_name, filename)
    return filename


def get_local_filepath(subdir: str, filename: str) -> str:
    """Get base filepath for USDA data for local reads."""
    return f"{LOCAL_BASE_PATH}/{BASE_PATH_SUFFIX}/{subdir}/{filename}"


def process_csv_food(row_values: list, dry_run: bool, write_fn: Callable) -> None:
    """Process CSV Food row values. Writes to database."""
    (fdc_id, data_type, description, _food_category_id, _publication_date) = row_values
    food_category_id: int | None = _food_category_id if _food_category_id else None
    publication_date: date | None = datetime.strptime(_publication_date, "%Y-%m-%d") if _publication_date else None
    write_fn(
        f"{usda_food.USDAFood.__name__}({fdc_id}, '{data_type}', '{description}', {food_category_id}, '{publication_date}'),"
    )

    if not dry_run:
        usda_food.update_or_create(
            fdc_id=fdc_id,
            defaults={
                "data_type": data_type,
                "description": description,
                "food_category_id": food_category_id,
                "publication_date": publication_date,
            },
        )


def process_csv_foundation_food(row_values: list, dry_run: bool, write_fn: Callable) -> None:
    """Process CSV foundation food row values. Writes to database."""
    fdc_id, ndb_number, footnote = row_values
    write_fn(f"{usda_foundation_food.USDAFoundationFood.__name__}({fdc_id}, '{ndb_number}', '{footnote}'),")

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_foundation_food.update_or_create(
            usda_food=cfood, defaults={"ndb_number": ndb_number, "footnote": footnote}
        )


def process_csv_sr_legacy(row_values: list, dry_run: bool, write_fn: Callable) -> None:
    """Process CSV SR legacy food row values. Writes to database."""
    fdc_id, ndb_number = row_values
    write_fn(f"{usda_sr_legacy.USDASRLegacy.__name__}({fdc_id}, '{ndb_number}'),")

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_sr_legacy.update_or_create(usda_food=cfood, defaults={"ndb_number": ndb_number})


def process_csv_fndds_food(row_values: list, dry_run: bool, write_fn: Callable) -> None:
    """Process CSV Survey FNDDS food row values. Writes to database."""
    (fdc_id, _food_code, _wweia_category_number, _start_date, _end_date) = row_values

    food_code: int | None = _food_code if _food_code else None
    wweia_category_number: int | None = _wweia_category_number if _wweia_category_number else None
    start_date: date | None = datetime.strptime(_start_date, "%Y-%m-%d") if _start_date else None
    end_date: date | None = datetime.strptime(_end_date, "%Y-%m-%d") if _end_date else None
    write_fn(
        f"{usda_fndds_food.USDAFnddsFood.__name__}({fdc_id}, {food_code}, {wweia_category_number}, '{start_date}', '{end_date}'),"
    )

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_fndds_food.update_or_create(
            usda_food=cfood,
            defaults={
                "food_code": food_code,
                "wweia_category_number": wweia_category_number,
                "start_date": start_date,
                "end_date": end_date,
            },
        )


def process_csv_branded_food(  # pylint: disable=too-many-locals
    row_values: list, dry_run: bool, write_fn: Callable
) -> None:
    """Process CSV Branded Food row values. Writes to database."""
    package_weight = None  # Added in October 2021
    preparation_state_code = None  # Added in April 2022
    trade_channel = None  # Added in April 2022
    if len(row_values) == 16:
        (
            fdc_id,
            brand_owner,
            brand_name,
            subbrand_name,
            gtin_upc,
            ingredients,
            not_a_significant_source_of,
            _serving_size,
            serving_size_unit,
            household_serving_fulltext,
            branded_food_category,
            data_source,
            _modified_date,
            _available_date,
            market_country,
            _discontinued_date,
        ) = row_values
    elif len(row_values) == 17:
        # October 2021 added package_weight in branded_foods. Ignore the field
        # for now, it's not in the schema PDF.
        (
            fdc_id,
            brand_owner,
            brand_name,
            subbrand_name,
            gtin_upc,
            ingredients,
            not_a_significant_source_of,
            _serving_size,
            serving_size_unit,
            household_serving_fulltext,
            branded_food_category,
            data_source,
            package_weight,
            _modified_date,
            _available_date,
            market_country,
            _discontinued_date,
        ) = row_values
    elif len(row_values) == 19:
        # April 2022 added preparation_state_code and trade_channel in branded_foods.
        (
            fdc_id,
            brand_owner,
            brand_name,
            subbrand_name,
            gtin_upc,
            ingredients,
            not_a_significant_source_of,
            _serving_size,
            serving_size_unit,
            household_serving_fulltext,
            branded_food_category,
            data_source,
            package_weight,
            _modified_date,
            _available_date,
            market_country,
            _discontinued_date,
            preparation_state_code,
            trade_channel,
        ) = row_values

    serving_size: float | None = _serving_size if _serving_size else None
    modified_date: date | None = datetime.strptime(_modified_date, "%Y-%m-%d") if _modified_date else None
    available_date: date | None = datetime.strptime(_available_date, "%Y-%m-%d") if _available_date else None
    discontinued_date: date | None = datetime.strptime(_discontinued_date, "%Y-%m-%d") if _discontinued_date else None
    write_fn(
        f"{usda_branded_food.USDABrandedFood.__name__}({fdc_id}, '{brand_owner}', '{brand_name}', '{subbrand_name}', '{gtin_upc}', '{ingredients}', '{not_a_significant_source_of}', {serving_size}, '{serving_size_unit}', '{household_serving_fulltext}', '{branded_food_category}', '{data_source}', '{package_weight}', '{modified_date}', '{available_date}', '{market_country}', '{discontinued_date}', '{preparation_state_code}', '{trade_channel}'"
    )

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_branded_food.update_or_create(
            usda_food=cfood,
            defaults={
                "brand_owner": brand_owner,
                "brand_name": brand_name,
                "subbrand_name": subbrand_name,
                "gtin_upc": gtin_upc,
                "ingredients": ingredients,
                "not_a_significant_source_of": not_a_significant_source_of,
                "serving_size": serving_size,
                "serving_size_unit": serving_size_unit,
                "household_serving_fulltext": household_serving_fulltext,
                "branded_food_category": branded_food_category,
                "data_source": data_source,
                "package_weight": package_weight,
                "modified_date": modified_date,
                "available_date": available_date,
                "market_country": market_country,
                "discontinued_date": discontinued_date,
                "preparation_state_code": preparation_state_code,
                "trade_channel": trade_channel,
            },
        )


def process_csv_food_nutrient(  # pylint: disable=too-many-locals
    row_values: list, dry_run: bool, write_fn: Callable
) -> None:
    """Process CSV food nutrient row values. Writes to database."""
    loq = None  # Added in April 2022
    if len(row_values) == 11:
        (
            id_,
            fdc_id,
            nutrient_id,
            _amount,
            _data_points,
            _derivation_id,
            _min_,
            _max_,
            _median,
            footnote,
            _min_year_acquired,
        ) = row_values
    elif len(row_values) == 12:
        # October 2021 added loq in food_nutrients. Ignore the field
        # for now, it's not in the schema PDF.
        (
            id_,
            fdc_id,
            nutrient_id,
            _amount,
            _data_points,
            _derivation_id,
            _min_,
            _max_,
            _median,
            loq,
            footnote,
            _min_year_acquired,
        ) = row_values

    amount: float | None = _amount if _amount else None
    data_points: int | None = _data_points if _data_points else None
    derivation_id: int | None = _derivation_id if _derivation_id else None
    min_: float | None = _min_ if _min_ else None
    max_: float | None = _max_ if _max_ else None
    median: float | None = _median if _median else None
    min_year_acquired: int | None = _min_year_acquired if _min_year_acquired else None
    write_fn(
        f"{usda_food_nutrient.USDAFoodNutrient.__name__}({id_}, {fdc_id}, {nutrient_id}, {amount}, {data_points}, {derivation_id}, {min_}, {max_}, {median}, {loq}, '{footnote}', {min_year_acquired}),"
    )

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_food_nutrient.update_or_create(
            id=id_,
            defaults={
                "usda_food": cfood,
                "nutrient_id": nutrient_id,
                "amount": amount,
                "data_points": data_points,
                "derivation_id": derivation_id,
                "min": min_,
                "max": max_,
                "median": median,
                "loq": loq,
                "footnote": footnote,
                "min_year_acquired": min_year_acquired,
            },
        )


def process_csv_food_portion(  # pylint: disable=too-many-locals
    row_values: list, dry_run: bool, write_fn: Callable
) -> None:
    """Process CSV food portion row values. Writes to database."""
    (
        id_,
        fdc_id,
        _seq_num,
        _amount,
        measure_unit_id,
        portion_description,
        modifier,
        gram_weight,
        _data_points,
        footnote,
        _min_year_acquired,
    ) = row_values

    amount: float | None = _amount if _amount else None
    seq_num: int | None = _seq_num if _seq_num else None
    data_points: int | None = _data_points if _data_points else None
    min_year_acquired: int | None = _min_year_acquired if _min_year_acquired else None
    write_fn(
        f"{usda_food_portion.USDAFoodPortion.__name__}({id_}, {fdc_id}, {seq_num}, {amount}, {measure_unit_id}, '{portion_description}', '{modifier}', {gram_weight}, {data_points}, '{footnote}', {min_year_acquired}),"
    )

    if not dry_run:
        cfood: usda_food.USDAFood | None = usda_food.load_cfood(fdc_id=fdc_id)
        usda_food_portion.update_or_create(
            id=id_,
            defaults={
                "usda_food": cfood,
                "seq_num": seq_num,
                "amount": amount,
                "measure_unit_id": measure_unit_id,
                "portion_description": portion_description,
                "modifier": modifier,
                "gram_weight": gram_weight,
                "data_points": data_points,
                "footnote": footnote,
                "min_year_acquired": min_year_acquired,
            },
        )


def process_csv_food_category(row_values: list, write_fn: Callable) -> None:
    """Process CSV food category row values. Writes to shell."""
    id_, code, description = row_values
    write_fn(f"{usda_config.USDAFoodCategory.__name__}({id_}, '{code}', '{description}'),")


def process_csv_wweia_food_category(row_values: list, write_fn: Callable) -> None:
    """Process CSV wwweia food category row values. Writes to shell."""
    id_, description = row_values
    write_fn(f"{usda_config.WWEIAFoodCategory.__name__}({id_}, '{description}'),")


def process_csv_measure_unit(row_values: list, write_fn: Callable) -> None:
    """Process CSV measure unit row values. Writes to shell."""
    if len(row_values) > 2:
        id_, name, abbreviation = row_values
    else:
        id_, name = row_values
        abbreviation = ""
    write_fn(f"{usda_config.USDAMeasureUnit.__name__}({id_}, '{name}', '{abbreviation}'),")


def process_csv_nutrient(row_values: list, write_fn: Callable) -> None:
    """Process CSV nutrient row values. Writes to shell."""
    id_, _name, unit_name, nutrient_nbr, _rank = row_values
    # Some nutrient names have single quotes, escape them.
    name: str = _name.replace("'", "\\'")
    rank: int | None = _rank if _rank else None
    write_fn(f"{usda_config.USDANutrient.__name__}({id_}, '{name}', '{unit_name}', '{nutrient_nbr}', {rank}),")


# flake8: noqa: C901
def process_file(  # pylint: disable=too-many-arguments,too-many-branches
    file_: TextIO, filename: str, start_line: int, num_lines: int, dry_run: bool, write_fn: Callable
) -> None:
    """Process CSV file."""
    write_fn(f"Processing {filename}:")
    if num_lines == -1:
        write_fn(f"From lines {start_line} to EOF")
    else:
        write_fn(f"{num_lines} lines starting from {start_line} line")

    write_fn("-" * 80)

    reader = csv.reader(file_, delimiter=",", quotechar='"')
    # Skip rows till start_line
    for _ in range(start_line):
        next(reader)

    for row_counter, row_values in enumerate(reader):
        if row_counter == num_lines:
            break

        if filename == CSV_FOOD:
            process_csv_food(row_values, dry_run, write_fn)
        elif filename == CSV_FOUNDATION_FOOD:
            process_csv_foundation_food(row_values, dry_run, write_fn)
        elif filename == CSV_FNDDS_FOOD:
            process_csv_fndds_food(row_values, dry_run, write_fn)
        elif filename == CSV_BRANDED_FOOD:
            process_csv_branded_food(row_values, dry_run, write_fn)
        elif filename == CSV_SR_LEGACY:
            process_csv_sr_legacy(row_values, dry_run, write_fn)
        elif filename == CSV_FOOD_NUTRIENT:
            process_csv_food_nutrient(row_values, dry_run, write_fn)
        elif filename == CSV_FOOD_PORTION:
            process_csv_food_portion(row_values, dry_run, write_fn)
        elif filename == CSV_FOOD_CATEGORY:
            process_csv_food_category(row_values, write_fn)
        elif filename == CSV_MEASURE_UNIT:
            process_csv_measure_unit(row_values, write_fn)
        elif filename == CSV_NUTRIENT:
            process_csv_nutrient(row_values, write_fn)
        elif filename == CSV_WWEIA_FOOD_CATEGORY:
            process_csv_wweia_food_category(row_values, write_fn)

    write_fn("-" * 80)


class Command(BaseCommand):
    """Import latest USDA data into the DB / Config"""

    help = "Import latest USDA data into the DB / Config"

    def add_arguments(self, parser: CommandParser) -> None:
        """Command arguments."""
        parser.add_argument("--type", type=int, nargs="?", const=0, default=0, help="usda_type")
        parser.add_argument("--ftype", type=int, nargs="?", const=0, default=0, help="file_type")
        # start defaults to 1, ignore header row in all files by default.
        parser.add_argument("--start", type=int, default=1, help="start")
        parser.add_argument("--lines", type=int, default=-1, help="lines")
        parser.add_argument("--remote", action="store_true", help="fetch data from remote (AWS S3)")
        parser.add_argument("--dry_run", action="store_true", help="dry run")

    def handle(self, *args: Any, **options: Any) -> None:
        """Run command."""
        usda_type: int = options["type"]
        file_type: int = options["ftype"]
        start_line: int = options["start"]
        num_lines: int = options["lines"]
        remote: bool = options["remote"]
        dry_run: bool = options["dry_run"]

        subdir: str = USDA_TYPE_MAP[usda_type]
        filenames: list[str] = CSV_TO_IMPORT[usda_type]

        if file_type:
            file_type_filename: str = FILE_TYPE_MAP[file_type]
            if file_type_filename not in filenames:
                self.stdout.write(f"{file_type_filename} not a valid filename for {subdir}")
                return

            filenames = [file_type_filename]

        for filename in filenames:
            filepath: str = get_filepath(remote, subdir, filename, self.stdout.write)
            with open(filepath, newline="", encoding="utf8") as file_:
                process_file(file_, filename, start_line, num_lines, dry_run, self.stdout.write)
                if os.path.exists(filename):
                    os.remove(filename)
