from __future__ import annotations

import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import (
    usda_branded_food,
    usda_fndds_food,
    usda_food,
    usda_food_nutrient,
    usda_food_portion,
    usda_foundation_food,
    usda_sr_legacy,
)

BASE_PATH_SUFFIX = "nutrition_tracker/tests/testdata/files/ingestion/sources/usda/April_2021"


def get_filepath(unused_remote, subdir, filename, unused_write):
    basepath = os.getcwd()
    return f"{basepath}/{BASE_PATH_SUFFIX}/{subdir}/{filename}"


class TestCommandUsdaDataImporter(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("usda_data_importer", *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()


@patch(target="nutrition_tracker.management.commands.usda_data_importer.get_filepath", wraps=get_filepath)
class TestCommandUsdaDataImporterDryRun(TestCommandUsdaDataImporter):
    def test_dry_run_all_foods(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=0)
        self.assertIn(
            "USDAFood(1, 'foundation_food', 'WESSON Vegetable Oil 1 GAL', 5, " "'2020-11-13 00:00:00'),", out
        )
        qs = usda_food.load_cfoods()
        self.assertEqual(0, qs.count())
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(0, qs.count())
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(0, qs.count())
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(0, qs.count())
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(0, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(0, qs.count())

    def test_dry_run_foundation_foods(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=1)
        self.assertIn("USDAFoundationFood(1, '12563', ' Other phytosterols = 34.67 mg/100g'),", out)
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(0, qs.count())

    def test_dry_run_sr_legacy_foods(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=2)
        self.assertIn("USDASRLegacy(17, '18634'),", out)
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(0, qs.count())

    def test_dry_run_fndds_foods(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=4)
        self.assertIn("USDAFnddsFood(12, 11000000, 9602, '2017-01-01 00:00:00', '2018-12-31 00:00:00'),", out)
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(0, qs.count())

    def test_dry_run_branded_foods(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=5)
        self.assertIn("USDABrandedFood(4, 'Richardson Oilseed Products (US) Limited', '',", out)
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())

    def test_dry_run_supporting_data(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=6)
        self.assertIn("USDAFoodCategory(1, '0100', 'Dairy and Egg Products'),", out)
        self.assertIn("USDAMeasureUnit(1000, 'cup', ''),", out)
        self.assertIn("USDANutrient(1001, 'Solids', 'G', '201', 200),", out)
        self.assertIn("WWEIAFoodCategory(1002, 'Milk, whole'),", out)
        qs = usda_food.load_cfoods()
        self.assertEqual(0, qs.count())
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(0, qs.count())
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(0, qs.count())
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(0, qs.count())
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(0, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(0, qs.count())


@patch(target="nutrition_tracker.management.commands.usda_data_importer.get_filepath", wraps=get_filepath)
class TestCommandUsdaDataImporterDryRunSubset(TestCommandUsdaDataImporter):
    def test_dry_run_all_foods_ftype_start_lines_set(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=0, ftype=2, start=2, lines=5)
        self.assertIn("USDAFoundationFood(2, '16158', '')", out)
        self.assertIn("USDAFoundationFood(3, '', 'ABC')", out)

    def test_dry_run_all_foods_ftype_lines_eof(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=0, ftype=2)
        self.assertIn("USDAFoundationFood(1, '12563', ' Other phytosterols = 34.67 mg/100g'),", out)
        self.assertIn("USDAFoundationFood(2, '16158', '')", out)
        self.assertIn("USDAFoundationFood(3, '', 'ABC')", out)

    def test_dry_run_all_foods_ftype_invalid(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=1, ftype=3)
        self.assertIn("sr_legacy_food.csv not a valid filename for Foundation_Foods", out)

    def test_dry_run_all_foods_ftype_default(self, mock_get_filepath):
        out = self.call_command(dry_run=True, type=1)
        self.assertIn("USDAFoundationFood(1, '12563', ' Other phytosterols = 34.67 mg/100g'),", out)


@patch(target="nutrition_tracker.management.commands.usda_data_importer.get_filepath", wraps=get_filepath)
class TestCommandUsdaDataImporterImportEmptyDB(TestCommandUsdaDataImporter):
    def test_import_all_foods_empty_db(self, mock_get_filepath):
        self.call_command(type=0)
        qs = usda_food.load_cfoods()
        self.assertEqual(19, qs.count())
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(3, qs.count())
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(2, qs.count())
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(5, qs.count())
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(8, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(19, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(11, qs.count())

    def test_import_foundation_foods_empty_db(self, mock_get_filepath):
        self.call_command(type=1)
        qs = usda_food.load_cfoods()
        self.assertEqual(19, qs.count())
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(3, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(19, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(11, qs.count())

    def test_import_sr_legacy_foods_empty_db(self, mock_get_filepath):
        self.call_command(type=2)
        qs = usda_food.load_cfoods()
        self.assertEqual(19, qs.count())
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(2, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(19, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(11, qs.count())

    def test_import_fndds_foods_empty_db(self, mock_get_filepath):
        self.call_command(type=4)
        qs = usda_food.load_cfoods()
        self.assertEqual(19, qs.count())
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(5, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(19, qs.count())
        qs = usda_food_portion.load_portions()
        self.assertEqual(11, qs.count())

    def test_import_branded_foods_empty_db(self, mock_get_filepath):
        self.call_command(type=5)
        qs = usda_food.load_cfoods()
        self.assertEqual(19, qs.count())
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(8, qs.count())
        qs = usda_food_nutrient.load_nutrients()
        self.assertEqual(19, qs.count())


@patch(target="nutrition_tracker.management.commands.usda_data_importer.get_filepath", wraps=get_filepath)
class TestCommandUsdaDataImporterImportExistingDB(TestCommandUsdaDataImporter):
    @classmethod
    def setUpTestData(cls):
        # Objects present in db, remains unchanged.
        cls.CFOOD_4 = usda_food.USDAFood.objects.create(
            fdc_id=4, data_type=constants.USDA_BRANDED_FOOD, description="SWANSON BROTH BEEF", food_category_id=5
        )

        # Objects to be updated with new data.
        cls.CFOOD_1 = usda_food.USDAFood.objects.create(
            fdc_id=1, data_type=constants.USDA_FOUNDATION_FOOD, description="WESSON Vegetable Oil 1 GAL"
        )
        cls.CFOOD_12 = usda_food.USDAFood.objects.create(
            fdc_id=12,
            data_type=constants.USDA_SURVEY_FNDDS_FOOD,
            description="CAMPBELL'S SLOW KETTLE SOUP CLAM CHOWDER",
        )
        cls.CFOOD_17 = usda_food.USDAFood.objects.create(
            fdc_id=17, data_type=constants.USDA_SR_LEGACY_FOOD, description="ABC", food_category_id=5
        )
        cls.FOUNDATION_FOOD_1 = usda_foundation_food.USDAFoundationFood.objects.create(usda_food_id=cls.CFOOD_1.fdc_id)
        cls.BRANDED_FOOD_4 = usda_branded_food.USDABrandedFood.objects.create(usda_food_id=cls.CFOOD_4.fdc_id)
        cls.FNDDS_FOOD_12 = usda_fndds_food.USDAFnddsFood.objects.create(usda_food_id=cls.CFOOD_12.fdc_id)
        cls.SR_LEGACY_FOOD_17 = usda_sr_legacy.USDASRLegacy.objects.create(usda_food_id=cls.CFOOD_17.fdc_id)

        # Objects present in db, but not in new data. Remains unchanged.
        cls.CFOOD_20 = usda_food.USDAFood.objects.create(
            fdc_id=20, data_type=constants.USDA_FOUNDATION_FOOD, description="Do not update"
        )
        cls.FOUNDATION_FOOD_20 = usda_foundation_food.USDAFoundationFood.objects.create(
            usda_food_id=cls.CFOOD_20.fdc_id
        )
        cls.SR_LEGACY_FOOD_20 = usda_sr_legacy.USDASRLegacy.objects.create(usda_food_id=cls.CFOOD_20.fdc_id)
        cls.FNDDS_FOOD_20 = usda_fndds_food.USDAFnddsFood.objects.create(usda_food_id=cls.CFOOD_20.fdc_id)
        cls.BRANDED_FOOD_20 = usda_branded_food.USDABrandedFood.objects.create(usda_food_id=cls.CFOOD_20.fdc_id)

    def test_import_all_foods_existing_db(self, mock_get_filepath):
        self.call_command(type=0)
        qs = usda_food.load_cfoods()
        self.assertEqual(20, qs.count())

        self.CFOOD_1.refresh_from_db()
        self.assertIsNotNone(self.CFOOD_1.food_category_id)
        self.CFOOD_12.refresh_from_db()
        self.assertIsNotNone(self.CFOOD_12.publication_date)
        self.CFOOD_17.refresh_from_db()
        self.assertIsNotNone(self.CFOOD_17.publication_date)
        self.CFOOD_20.refresh_from_db()
        self.assertIsNone(self.CFOOD_20.food_category_id)

    def test_foundation_foods_existing_db(self, mock_get_filepath):
        self.call_command(type=1)
        qs = usda_foundation_food.load_foundation_foods()
        self.assertEqual(4, qs.count())

        self.FOUNDATION_FOOD_1.refresh_from_db()
        self.assertIsNotNone(self.FOUNDATION_FOOD_1.ndb_number)
        self.FOUNDATION_FOOD_20.refresh_from_db()
        self.assertIsNone(self.FOUNDATION_FOOD_20.ndb_number)

    def test_sr_legacy_foods_existing_db(self, mock_get_filepath):
        self.call_command(type=2)
        qs = usda_sr_legacy.load_sr_legacy_foods()
        self.assertEqual(3, qs.count())

        self.SR_LEGACY_FOOD_17.refresh_from_db()
        self.assertIsNotNone(self.SR_LEGACY_FOOD_17.ndb_number)
        self.SR_LEGACY_FOOD_20.refresh_from_db()
        self.assertIsNone(self.SR_LEGACY_FOOD_20.ndb_number)

    def test_fndds_foods_existing_db(self, mock_get_filepath):
        self.call_command(type=4)
        qs = usda_fndds_food.load_fndds_foods()
        self.assertEqual(6, qs.count())

        self.FNDDS_FOOD_12.refresh_from_db()
        self.assertIsNotNone(self.FNDDS_FOOD_12.food_code)
        self.FNDDS_FOOD_20.refresh_from_db()
        self.assertIsNone(self.FNDDS_FOOD_20.food_code)

    def test_branded_foods_existing_db(self, mock_get_filepath):
        self.call_command(type=5)
        qs = usda_branded_food.load_cbranded_foods()
        self.assertEqual(9, qs.count())

        self.BRANDED_FOOD_4.refresh_from_db()
        self.assertIsNotNone(self.BRANDED_FOOD_4.brand_owner)
        self.BRANDED_FOOD_20.refresh_from_db()
        self.assertIsNone(self.BRANDED_FOOD_20.brand_owner)
