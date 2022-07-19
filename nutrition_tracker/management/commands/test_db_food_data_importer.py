from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.test import TransactionTestCase
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.management.commands import db_food_data_importer
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
from nutrition_tracker.tests import objects as test_objects


class TestCommandDBFoodImporter(TransactionTestCase):
    reset_sequences = True

    def test_should_import_usda_food_no_energy_fails(self):
        cfood = test_objects.get_usda_food()
        self.assertFalse(db_food_data_importer.should_import_usda_food(cfood))

    def test_should_import_usda_food_unknown_type_fails(self):
        cfood = test_objects.get_usda_food_unknown_type()
        self.assertFalse(db_food_data_importer.should_import_usda_food(cfood))

    def test_should_import_usda_food(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_branded_food()
        test_objects.get_usda_food_nutrient()
        self.assertTrue(db_food_data_importer.should_import_usda_food(cfood))

    def test_should_import_usda_foundation_food_success_default(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_foundation_food()
        cfood.data_type = constants.USDA_FOUNDATION_FOOD
        cfood.save()
        cfood.refresh_from_db()
        self.assertTrue(db_food_data_importer.should_import_usda_foundation_food(cfood))

    def test_should_import_usda_foundation_food_success_with_clash(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_foundation_food()
        cfood.data_type = constants.USDA_FOUNDATION_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()

        self.assertTrue(db_food_data_importer.should_import_usda_foundation_food(cfood))

    def test_should_import_usda_foundation_food_fails_with_clash(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_foundation_food()
        cfood.data_type = constants.USDA_FOUNDATION_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()

        self.assertFalse(db_food_data_importer.should_import_usda_foundation_food(cfood_2))

    def test_should_import_usda_sr_legacy_food_success_default(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_sr_legacy_food()
        cfood.data_type = constants.USDA_SR_LEGACY_FOOD
        cfood.save()
        cfood.refresh_from_db()
        self.assertTrue(db_food_data_importer.should_import_usda_sr_legacy_food(cfood))

    def test_should_import_usda_sr_legacy_food_fails_foundation_food_same_name(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_sr_legacy_food()
        cfood.data_type = constants.USDA_SR_LEGACY_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_sr_legacy_food(cfood))

    def test_should_import_usda_sr_legacy_food_fails_foundation_food_different_name_same_ndb_number(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_sr_legacy_food()
        cfood.data_type = constants.USDA_SR_LEGACY_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        usda_foundation_food.create(usda_food=cfood_2, ndb_number="123")
        self.assertFalse(db_food_data_importer.should_import_usda_sr_legacy_food(cfood))

    def test_should_import_usda_survey_fndds_food_success_default(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_fndds_food()
        cfood.data_type = constants.USDA_SURVEY_FNDDS_FOOD
        cfood.save()
        cfood.refresh_from_db()
        self.assertTrue(db_food_data_importer.should_import_usda_survey_fndds_food(cfood))

    def test_should_import_usda_survey_fndds_food_fails_foundation_food_same_name(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_fndds_food()
        cfood.data_type = constants.USDA_SURVEY_FNDDS_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_survey_fndds_food(cfood))

    def test_should_import_usda_survey_fndds_food_fails_sr_legacy_food_same_name(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_fndds_food()
        cfood.data_type = constants.USDA_SURVEY_FNDDS_FOOD
        cfood.save()
        cfood.refresh_from_db()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_SR_LEGACY_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_survey_fndds_food(cfood))

    def test_should_import_usda_branded_food_success_default(self):
        test_objects.get_usda_food()
        cbranded_food = test_objects.get_usda_branded_food()
        cbranded_food.gtin_upc = None
        cbranded_food.save()
        cfood = usda_food.load_cfood(fdc_id=cbranded_food.usda_food.fdc_id)
        self.assertTrue(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_fails_foundation_food_same_name(self):
        test_objects.get_usda_food()
        cbranded_food = test_objects.get_usda_branded_food()
        cbranded_food.gtin_upc = None
        cbranded_food.save()
        cfood = usda_food.load_cfood(fdc_id=cbranded_food.usda_food.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_fails_sr_legacy_food_same_name(self):
        test_objects.get_usda_food()
        cbranded_food = test_objects.get_usda_branded_food()
        cbranded_food.gtin_upc = None
        cbranded_food.save()
        cfood = usda_food.load_cfood(fdc_id=cbranded_food.usda_food.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_SR_LEGACY_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_fails_fndds_food_same_name(self):
        test_objects.get_usda_food()
        cbranded_food = test_objects.get_usda_branded_food()
        cbranded_food.gtin_upc = None
        cbranded_food.save()
        cfood = usda_food.load_cfood(fdc_id=cbranded_food.usda_food.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.description = "test"
        cfood_2.data_type = constants.USDA_SURVEY_FNDDS_FOOD
        cfood_2.save()
        cfood_2.refresh_from_db()
        self.assertFalse(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_fails_multiple_upc_old_available_date(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_branded_food()
        cfood = usda_food.load_cfood(fdc_id=cfood.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.data_type = constants.USDA_BRANDED_FOOD
        cfood_2.save()
        usda_branded_food.create(
            usda_food=cfood_2, brand_name="brand", gtin_upc="usda_upc", available_date=timezone.localdate()
        )
        cfood_2 = usda_food.load_cfood(fdc_id=cfood_2.fdc_id)
        self.assertFalse(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_success_multiple_upc_latest_available_date(self):
        cfood = test_objects.get_usda_food()
        cbranded_food = test_objects.get_usda_branded_food()
        cbranded_food.available_date = timezone.localdate()
        cbranded_food.save()
        cfood = usda_food.load_cfood(fdc_id=cfood.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.data_type = constants.USDA_BRANDED_FOOD
        cfood_2.save()
        usda_branded_food.create(
            usda_food=cfood_2,
            brand_name="brand",
            gtin_upc="usda_upc",
            available_date=timezone.localdate() - timezone.timedelta(days=1),
        )
        cfood_2 = usda_food.load_cfood(fdc_id=cfood_2.fdc_id)
        self.assertTrue(db_food_data_importer.should_import_usda_branded_food(cfood))

    def test_should_import_usda_branded_food_fails_multiple_upc_same_available_date_fewer_nutrients(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_branded_food()
        test_objects.get_usda_food_nutrient()
        cfood = usda_food.load_cfood(fdc_id=cfood.fdc_id)

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.data_type = constants.USDA_BRANDED_FOOD
        cfood_2.save()
        usda_branded_food.create(usda_food=cfood_2, brand_name="brand", gtin_upc="usda_upc")
        usda_food_nutrient.create(id=9, usda_food=cfood_2, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=100)
        usda_food_nutrient.create(id=10, usda_food=cfood_2, nutrient_id=constants.FAT_NUTRIENT_ID, amount=44)
        cfood_2 = usda_food.load_cfood(fdc_id=cfood_2.fdc_id)
        self.assertFalse(db_food_data_importer.should_import_usda_branded_food(cfood))


class TestCommandDBFoodDataImporter(TransactionTestCase):
    reset_sequences = True

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("db_food_data_importer", *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()


class TestCommandDBFoodDataImporterDryRun(TestCommandDBFoodDataImporter):
    def test_dry_run_defaults(self):
        out = self.call_command(dry_run=True)
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(0, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(0, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(0, qs.count())

    def test_dry_run_usda(self):
        out = self.call_command(dry_run=True, stypes=[1])
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(0, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(0, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(0, qs.count())

    def test_dry_run_usda_foundation_foods(self):
        out = self.call_command(dry_run=True, stypes=[1], subtypes=[1])
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(0, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(0, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(0, qs.count())

    def test_writes_usda_foundation_food(self):
        cfood = test_objects.get_usda_food()
        test_objects.get_usda_food_nutrient()
        test_objects.get_usda_food_portion()
        test_objects.get_usda_foundation_food()
        cfood.data_type = constants.USDA_FOUNDATION_FOOD
        cfood.save()

        out = self.call_command()
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(1, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(1, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(1, qs.count())

    def test_writes_usda_branded_food(self):
        test_objects.get_usda_food()
        test_objects.get_usda_branded_food()
        test_objects.get_usda_food_nutrient()
        test_objects.get_usda_food_portion()

        out = self.call_command()
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(1, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(1, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(1, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(2, qs.count())

    def test_writes_with_offset(self):
        test_objects.get_usda_food()
        test_objects.get_usda_branded_food()
        test_objects.get_usda_food_nutrient()
        test_objects.get_usda_food_portion()

        cfood_2 = test_objects.get_usda_food_2()
        cfood_2.data_type = constants.USDA_FOUNDATION_FOOD
        cfood_2.save()
        test_objects.get_usda_food_2_nutrient()
        test_objects.get_usda_food_portion_2()

        out = self.call_command(stypes=[1], start=1, rows=4)
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(1, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(0, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(1, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(1, qs.count())

        out = self.call_command(stypes=[1], start=0, rows=4)
        self.assertIn("Processing USDA Foods", out)
        qs = db_food.load_cfoods()
        self.assertEqual(2, qs.count())
        qs = db_branded_food.load_cbranded_foods()
        self.assertEqual(1, qs.count())
        qs = db_food_nutrient.load_nutrients()
        self.assertEqual(2, qs.count())
        qs = db_food_portion.load_portions()
        self.assertEqual(3, qs.count())
