"""Config classes and constants for FDA Nutrition data."""
from __future__ import annotations

import dataclasses

from nutrition_tracker.constants import constants


@dataclasses.dataclass
class FDANutrientRDI:
    """Wrapper class for FDA Nutrition RDI values."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        nutrient_id: int,
        adult: float | None,
        infant: float | None,
        children: float | None,
        pregnant: float | None,
        threshold: constants.Threshold | None = None,
    ) -> None:
        self.nutrient_id = nutrient_id
        # Adult / Children >= 4
        self.adult = adult
        # Infants through 12 months
        self.infant = infant
        # Children 1 through 3 years
        self.children = children
        # Pregnant and lactating women
        self.pregnant = pregnant
        self.threshold = threshold


fda_nutrient_rdis: list[FDANutrientRDI] = [
    # Macro nutrient recommendations based on
    # https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/cfrsearch.cfm?fr=101.9
    FDANutrientRDI(constants.ENERGY_NUTRIENT_ID, 2000, 1000, 1000, 2000, constants.Threshold.MAX_VALUE),
    FDANutrientRDI(constants.PROTEIN_NUTRIENT_ID, 50, 11, 13, 71, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.FAT_NUTRIENT_ID, 78, 30, 39, 78, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.CARBOHYDRATE_NUTRIENT_ID, 275, 95, 150, 275, constants.Threshold.MAX_VALUE),
    FDANutrientRDI(constants.TOTAL_FIBER_NUTRIENT_ID, 28, None, 14, 28, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.ADDED_SUGARS_NUTRIENT_ID, 50, None, 25, 50, constants.Threshold.MAX_VALUE),
    FDANutrientRDI(constants.SATURATED_FAT_NUTRIENT_ID, 20, None, 10, 20, constants.Threshold.MAX_VALUE),
    FDANutrientRDI(constants.CHOLESTEROL_NUTRIENT_ID, 300, None, 300, 300, constants.Threshold.MAX_VALUE),
    FDANutrientRDI(constants.SODIUM_NUTRIENT_ID, 2300, 570, 1500, 2300, constants.Threshold.MAX_VALUE),
    # From https://www.fda.gov/media/99069/download
    FDANutrientRDI(constants.VITAMIN_D_NUTRIENT_ID, 20, 10, 15, 15, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.CALCIUM_NUTRIENT_ID, 1300, 260, 700, 1300, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.IRON_NUTRIENT_ID, 18, 11, 7, 27, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.POTASSIUM_NUTRIENT_ID, 4700, 700, 3000, 5100, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_A_NUTRIENT_ID, 900, 500, 300, 1300, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_C_NUTRIENT_ID, 90, 50, 15, 120, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_E_NUTRIENT_ID, 15, 5, 6, 19, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_K_NUTRIENT_ID, 120, 2.5, 30, 90, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.THIAMIN_NUTRIENT_ID, 1.2, 0.3, 0.5, 1.4, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.RIBOFLAVIN_NUTRIENT_ID, 1.3, 0.4, 0.5, 1.6, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.NIACIN_NUTRIENT_ID, 16, 4, 6, 18, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_B6_NUTRIENT_ID, 1.7, 0.3, 0.5, 2, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.FOLATE_NUTRIENT_ID, 400, 80, 150, 600, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.VITAMIN_B12_NUTRIENT_ID, 2.4, 0.5, 0.9, 2.8, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.BIOTIN_NUTRIENT_ID, 30, 6, 8, 35, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.PANTOTHENIC_ACID_NUTRIENT_ID, 5, 1.8, 2, 7, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.PHOSPHORUS_NUTRIENT_ID, 1250, 275, 460, 1250, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.IODINE_NUTRIENT_ID, 150, 130, 90, 290, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.MAGNESIUM_NUTRIENT_ID, 420, 75, 80, 400, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.ZINC_NUTRIENT_ID, 11, 3, 3, 13, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.SELENIUM_NUTRIENT_ID, 55, 20, 20, 70, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.COPPER_NUTRIENT_ID, 0.9, 0.2, 0.3, 1.3, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.MANGANESE_NUTRIENT_ID, 2.3, 0.6, 1.2, 2.6, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.CHROMIUM_NUTRIENT_ID, 35, 5.5, 11, 45, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.MOLYBDENUM_NUTRIENT_ID, 45, 3, 17, 50, constants.Threshold.MIN_VALUE),
    FDANutrientRDI(constants.CHOLINE_NUTRIENT_ID, 550, 150, 200, 550, constants.Threshold.MIN_VALUE),
]
