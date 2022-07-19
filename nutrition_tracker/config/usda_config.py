# pylint: disable=too-many-lines
"""Config classes and constants for USDA data."""
from __future__ import annotations

import dataclasses

from nutrition_tracker.constants import constants


@dataclasses.dataclass
class USDAFoodCategory:
    """Wrapper class for USDA Food Category."""

    def __init__(self, id_: int, code: str | None, description: str) -> None:
        self.id_ = id_
        self.code = code
        self.description = description


usda_food_categories: list[USDAFoodCategory] = [
    USDAFoodCategory(constants.CATEGORY_ALL_FOODS, None, "All Foods"),
    USDAFoodCategory(1, "0100", "Dairy and Egg Products"),
    USDAFoodCategory(2, "0200", "Spices and Herbs"),
    USDAFoodCategory(3, "0300", "Baby Foods"),
    USDAFoodCategory(4, "0400", "Fats and Oils"),
    USDAFoodCategory(5, "0500", "Poultry Products"),
    USDAFoodCategory(6, "0600", "Soups, Sauces, and Gravies"),
    USDAFoodCategory(7, "0700", "Sausages and Luncheon Meats"),
    USDAFoodCategory(8, "0800", "Breakfast Cereals"),
    USDAFoodCategory(9, "0900", "Fruits and Fruit Juices"),
    USDAFoodCategory(10, "1000", "Pork Products"),
    USDAFoodCategory(11, "1100", "Vegetables and Vegetable Products"),
    USDAFoodCategory(12, "1200", "Nut and Seed Products"),
    USDAFoodCategory(13, "1300", "Beef Products"),
    USDAFoodCategory(14, "1400", "Beverages"),
    USDAFoodCategory(15, "1500", "Finfish and Shellfish Products"),
    USDAFoodCategory(16, "1600", "Legumes and Legume Products"),
    USDAFoodCategory(17, "1700", "Lamb, Veal, and Game Products"),
    USDAFoodCategory(18, "1800", "Baked Products"),
    USDAFoodCategory(19, "1900", "Sweets"),
    USDAFoodCategory(20, "2000", "Cereal Grains and Pasta"),
    USDAFoodCategory(21, "2100", "Fast Foods"),
    USDAFoodCategory(22, "2200", "Meals, Entrees, and Side Dishes"),
    USDAFoodCategory(23, "2500", "Snacks"),
    USDAFoodCategory(24, "3500", "American Indian/Alaska Native Foods"),
    USDAFoodCategory(25, "3600", "Restaurant Foods"),
    USDAFoodCategory(26, "4500", "Branded Food Products Database"),
    USDAFoodCategory(27, "2600", "Quality Control Materials"),
    USDAFoodCategory(28, "1410", "Alcoholic Beverages"),
]


@dataclasses.dataclass
class WWEIAFoodCategory:
    """Wrapper class for USDA WWEIA Food Category."""

    def __init__(self, id_: int, description: str) -> None:
        self.id_ = id_
        self.description = description


wweia_food_categories: list[WWEIAFoodCategory] = [
    WWEIAFoodCategory(1002, "Milk, whole"),
    WWEIAFoodCategory(1004, "Milk, reduced fat"),
    WWEIAFoodCategory(1006, "Milk, lowfat"),
    WWEIAFoodCategory(1008, "Milk, nonfat"),
    WWEIAFoodCategory(1202, "Flavored milk, whole"),
    WWEIAFoodCategory(1204, "Flavored milk, reduced fat"),
    WWEIAFoodCategory(1206, "Flavored milk, lowfat"),
    WWEIAFoodCategory(1208, "Flavored milk, nonfat"),
    WWEIAFoodCategory(1402, "Milk shakes and other dairy drinks"),
    WWEIAFoodCategory(1404, "Milk substitutes"),
    WWEIAFoodCategory(1602, "Cheese"),
    WWEIAFoodCategory(1604, "Cottage/ricotta cheese"),
    WWEIAFoodCategory(1820, "Yogurt, regular"),
    WWEIAFoodCategory(1822, "Yogurt, Greek"),
    WWEIAFoodCategory(2002, "Beef, excludes ground"),
    WWEIAFoodCategory(2004, "Ground beef"),
    WWEIAFoodCategory(2006, "Pork"),
    WWEIAFoodCategory(2008, "Lamb, goat, game"),
    WWEIAFoodCategory(2010, "Liver and organ meats"),
    WWEIAFoodCategory(2202, "Chicken, whole pieces"),
    WWEIAFoodCategory(2204, "Chicken patties, nuggets and tenders"),
    WWEIAFoodCategory(2206, "Turkey, duck, other poultry"),
    WWEIAFoodCategory(2402, "Fish"),
    WWEIAFoodCategory(2404, "Shellfish"),
    WWEIAFoodCategory(2502, "Eggs and omelets"),
    WWEIAFoodCategory(2602, "Cold cuts and cured meats"),
    WWEIAFoodCategory(2604, "Bacon"),
    WWEIAFoodCategory(2606, "Frankfurters"),
    WWEIAFoodCategory(2608, "Sausages"),
    WWEIAFoodCategory(2802, "Beans, peas, legumes"),
    WWEIAFoodCategory(2804, "Nuts and seeds"),
    WWEIAFoodCategory(2806, "Processed soy products"),
    WWEIAFoodCategory(3002, "Meat mixed dishes"),
    WWEIAFoodCategory(3004, "Poultry mixed dishes"),
    WWEIAFoodCategory(3006, "Seafood mixed dishes"),
    WWEIAFoodCategory(3102, "Bean, pea, legume dishes"),
    WWEIAFoodCategory(3104, "Vegetable dishes"),
    WWEIAFoodCategory(3202, "Rice mixed dishes"),
    WWEIAFoodCategory(3204, "Pasta mixed dishes, excludes macaroni and cheese"),
    WWEIAFoodCategory(3206, "Macaroni and cheese"),
    WWEIAFoodCategory(3208, "Turnovers and other grain-based items"),
    WWEIAFoodCategory(3402, "Fried rice and lo/chow mein"),
    WWEIAFoodCategory(3404, "Stir-fry and soy-based sauce mixtures"),
    WWEIAFoodCategory(3406, "Egg rolls, dumplings, sushi"),
    WWEIAFoodCategory(3502, "Burritos and tacos"),
    WWEIAFoodCategory(3504, "Nachos"),
    WWEIAFoodCategory(3506, "Other Mexican mixed dishes"),
    WWEIAFoodCategory(3602, "Pizza"),
    WWEIAFoodCategory(3702, "Burgers (single code)"),
    WWEIAFoodCategory(3703, "Frankfurter sandwiches (single code)"),
    WWEIAFoodCategory(3704, "Chicken/turkey sandwiches (single code)"),
    WWEIAFoodCategory(3706, "Egg/breakfast sandwiches (single code)"),
    WWEIAFoodCategory(3708, "Other sandwiches (single code)"),
    WWEIAFoodCategory(3720, "Cheese sandwiches (single code)"),
    WWEIAFoodCategory(3722, "Peanut butter and jelly sandwiches (single code)"),
    WWEIAFoodCategory(3730, "Seafood sandwiches (single code)"),
    WWEIAFoodCategory(3802, "Soups"),
    WWEIAFoodCategory(4002, "Rice"),
    WWEIAFoodCategory(4004, "Pasta, noodles, cooked grains"),
    WWEIAFoodCategory(4202, "Yeast breads"),
    WWEIAFoodCategory(4204, "Rolls and buns"),
    WWEIAFoodCategory(4206, "Bagels and English muffins"),
    WWEIAFoodCategory(4208, "Tortillas"),
    WWEIAFoodCategory(4402, "Biscuits, muffins, quick breads"),
    WWEIAFoodCategory(4404, "Pancakes, waffles, French toast"),
    WWEIAFoodCategory(4602, "Ready-to-eat cereal, higher sugar (>21.2g/100g)"),
    WWEIAFoodCategory(4604, "Ready-to-eat cereal, lower sugar (=<21.2g/100g)"),
    WWEIAFoodCategory(4802, "Oatmeal"),
    WWEIAFoodCategory(4804, "Grits and other cooked cereals"),
    WWEIAFoodCategory(5002, "Potato chips"),
    WWEIAFoodCategory(5004, "Tortilla, corn, other chips"),
    WWEIAFoodCategory(5006, "Popcorn"),
    WWEIAFoodCategory(5008, "Pretzels/snack mix"),
    WWEIAFoodCategory(5202, "Crackers, excludes saltines"),
    WWEIAFoodCategory(5204, "Saltine crackers"),
    WWEIAFoodCategory(5402, "Cereal bars"),
    WWEIAFoodCategory(5404, "Nutrition bars"),
    WWEIAFoodCategory(5502, "Cakes and pies"),
    WWEIAFoodCategory(5504, "Cookies and brownies"),
    WWEIAFoodCategory(5506, "Doughnuts, sweet rolls, pastries"),
    WWEIAFoodCategory(5702, "Candy containing chocolate"),
    WWEIAFoodCategory(5704, "Candy not containing chocolate"),
    WWEIAFoodCategory(5802, "Ice cream and frozen dairy desserts"),
    WWEIAFoodCategory(5804, "Pudding"),
    WWEIAFoodCategory(5806, "Gelatins, ices, sorbets"),
    WWEIAFoodCategory(6002, "Apples"),
    WWEIAFoodCategory(6004, "Bananas"),
    WWEIAFoodCategory(6006, "Grapes"),
    WWEIAFoodCategory(6008, "Peaches and nectarines"),
    WWEIAFoodCategory(6009, "Strawberries"),
    WWEIAFoodCategory(6011, "Blueberries and other berries"),
    WWEIAFoodCategory(6012, "Citrus fruits"),
    WWEIAFoodCategory(6014, "Melons"),
    WWEIAFoodCategory(6016, "Dried fruits"),
    WWEIAFoodCategory(6018, "Other fruits and fruit salads"),
    WWEIAFoodCategory(6020, "Pears"),
    WWEIAFoodCategory(6022, "Pineapple"),
    WWEIAFoodCategory(6024, "Mango and papaya"),
    WWEIAFoodCategory(6402, "Tomatoes"),
    WWEIAFoodCategory(6404, "Carrots"),
    WWEIAFoodCategory(6406, "Other red and orange vegetables"),
    WWEIAFoodCategory(6407, "Broccoli"),
    WWEIAFoodCategory(6409, "Spinach"),
    WWEIAFoodCategory(6410, "Lettuce and lettuce salads"),
    WWEIAFoodCategory(6411, "Other dark green vegetables"),
    WWEIAFoodCategory(6412, "String beans"),
    WWEIAFoodCategory(6413, "Cabbage"),
    WWEIAFoodCategory(6414, "Onions"),
    WWEIAFoodCategory(6416, "Corn"),
    WWEIAFoodCategory(6418, "Other starchy vegetables"),
    WWEIAFoodCategory(6420, "Other vegetables and combinations"),
    WWEIAFoodCategory(6430, "Fried vegetables"),
    WWEIAFoodCategory(6432, "Coleslaw, non-lettuce salads"),
    WWEIAFoodCategory(6489, "Vegetables on a sandwich"),
    WWEIAFoodCategory(6802, "White potatoes, baked or boiled"),
    WWEIAFoodCategory(6804, "French fries and other fried white potatoes"),
    WWEIAFoodCategory(6806, "Mashed potatoes and white potato mixtures"),
    WWEIAFoodCategory(7002, "Citrus juice"),
    WWEIAFoodCategory(7004, "Apple juice"),
    WWEIAFoodCategory(7006, "Other fruit juice"),
    WWEIAFoodCategory(7008, "Vegetable juice"),
    WWEIAFoodCategory(7102, "Diet soft drinks"),
    WWEIAFoodCategory(7104, "Diet sport and energy drinks"),
    WWEIAFoodCategory(7106, "Other diet drinks"),
    WWEIAFoodCategory(7202, "Soft drinks"),
    WWEIAFoodCategory(7204, "Fruit drinks"),
    WWEIAFoodCategory(7206, "Sport and energy drinks"),
    WWEIAFoodCategory(7208, "Nutritional beverages"),
    WWEIAFoodCategory(7220, "Smoothies and grain drinks"),
    WWEIAFoodCategory(7302, "Coffee"),
    WWEIAFoodCategory(7304, "Tea"),
    WWEIAFoodCategory(7502, "Beer"),
    WWEIAFoodCategory(7504, "Wine"),
    WWEIAFoodCategory(7506, "Liquor and cocktails"),
    WWEIAFoodCategory(7702, "Tap water"),
    WWEIAFoodCategory(7704, "Bottled water"),
    WWEIAFoodCategory(7802, "Flavored or carbonated water"),
    WWEIAFoodCategory(7804, "Enhanced or fortified water"),
    WWEIAFoodCategory(8002, "Butter and animal fats"),
    WWEIAFoodCategory(8004, "Margarine"),
    WWEIAFoodCategory(8006, "Cream cheese, sour cream, whipped cream"),
    WWEIAFoodCategory(8008, "Cream and cream substitutes"),
    WWEIAFoodCategory(8010, "Mayonnaise"),
    WWEIAFoodCategory(8012, "Salad dressings and vegetable oils"),
    WWEIAFoodCategory(8402, "Tomato-based condiments"),
    WWEIAFoodCategory(8404, "Soy-based condiments"),
    WWEIAFoodCategory(8406, "Mustard and other condiments"),
    WWEIAFoodCategory(8408, "Olives, pickles, pickled vegetables"),
    WWEIAFoodCategory(8410, "Pasta sauces, tomato-based"),
    WWEIAFoodCategory(8412, "Dips, gravies, other sauces"),
    WWEIAFoodCategory(8802, "Sugars and honey"),
    WWEIAFoodCategory(8804, "Sugar substitutes"),
    WWEIAFoodCategory(8806, "Jams, syrups, toppings"),
    WWEIAFoodCategory(9002, "Baby food: cereals"),
    WWEIAFoodCategory(9004, "Baby food: fruit"),
    WWEIAFoodCategory(9006, "Baby food: vegetable"),
    WWEIAFoodCategory(9008, "Baby food: meat and dinners"),
    WWEIAFoodCategory(9010, "Baby food: yogurt"),
    WWEIAFoodCategory(9012, "Baby food: snacks and sweets"),
    WWEIAFoodCategory(9202, "Baby juice"),
    WWEIAFoodCategory(9204, "Baby water"),
    WWEIAFoodCategory(9402, "Formula, ready-to-feed"),
    WWEIAFoodCategory(9404, "Formula, prepared from powder"),
    WWEIAFoodCategory(9406, "Formula, prepared from concentrate"),
    WWEIAFoodCategory(9602, "Human milk"),
    WWEIAFoodCategory(9802, "Protein and nutritional powders"),
    WWEIAFoodCategory(9999, "Not included in a food category"),
]


@dataclasses.dataclass
class USDAMeasureUnit:
    """Wrapper class for USDA Measure Unit."""

    def __init__(self, id_: int, name: str, abbreviation: str) -> None:
        self.id_ = id_
        self.name = name
        self.abbreviation = abbreviation


usda_measure_units: list[USDAMeasureUnit] = [
    USDAMeasureUnit(1000, "cup", ""),
    USDAMeasureUnit(1001, "tablespoon", "tbsp"),
    USDAMeasureUnit(1002, "teaspoon", "tsp"),
    USDAMeasureUnit(1003, "liter", ""),
    USDAMeasureUnit(1004, "milliliter", "ml"),
    USDAMeasureUnit(1005, "cubic inch", "cu"),
    USDAMeasureUnit(1006, "cubic centimeter", "cc"),
    USDAMeasureUnit(1007, "gallon", ""),
    USDAMeasureUnit(1008, "pint", ""),
    USDAMeasureUnit(1009, "fl oz", ""),
    USDAMeasureUnit(1010, "paired cooked w", ""),
    USDAMeasureUnit(1011, "paired raw w", ""),
    USDAMeasureUnit(1012, "dripping w", ""),
    USDAMeasureUnit(1013, "bar", ""),
    USDAMeasureUnit(1014, "bird", ""),
    USDAMeasureUnit(1015, "biscuit", ""),
    USDAMeasureUnit(1016, "bottle", ""),
    USDAMeasureUnit(1017, "box", ""),
    USDAMeasureUnit(1018, "breast", ""),
    USDAMeasureUnit(1019, "can", ""),
    USDAMeasureUnit(1020, "chicken", ""),
    USDAMeasureUnit(1021, "chop", ""),
    USDAMeasureUnit(1022, "cookie", ""),
    USDAMeasureUnit(1023, "container", ""),
    USDAMeasureUnit(1024, "cracker", ""),
    USDAMeasureUnit(1025, "drink", ""),
    USDAMeasureUnit(1026, "drumstick", ""),
    USDAMeasureUnit(1027, "fillet", ""),
    USDAMeasureUnit(1028, "fruit", ""),
    USDAMeasureUnit(1029, "large", ""),
    USDAMeasureUnit(1030, "lb", ""),
    USDAMeasureUnit(1031, "leaf", ""),
    USDAMeasureUnit(1032, "leg", ""),
    USDAMeasureUnit(1033, "link", ""),
    USDAMeasureUnit(1034, "links", ""),
    USDAMeasureUnit(1035, "loaf", ""),
    USDAMeasureUnit(1036, "medium", ""),
    USDAMeasureUnit(1037, "muffin", ""),
    USDAMeasureUnit(1038, "oz", ""),
    USDAMeasureUnit(1039, "package", ""),
    USDAMeasureUnit(1040, "packet", ""),
    USDAMeasureUnit(1041, "patty", ""),
    USDAMeasureUnit(1042, "patties", ""),
    USDAMeasureUnit(1043, "piece", ""),
    USDAMeasureUnit(1044, "pieces", ""),
    USDAMeasureUnit(1045, "quart", ""),
    USDAMeasureUnit(1046, "roast", ""),
    USDAMeasureUnit(1047, "sausage", ""),
    USDAMeasureUnit(1048, "scoop", ""),
    USDAMeasureUnit(1049, "serving", ""),
    USDAMeasureUnit(1050, "slice", ""),
    USDAMeasureUnit(1051, "slices", ""),
    USDAMeasureUnit(1052, "small", ""),
    USDAMeasureUnit(1053, "stalk", ""),
    USDAMeasureUnit(1054, "steak", ""),
    USDAMeasureUnit(1055, "stick", ""),
    USDAMeasureUnit(1056, "strip", ""),
    USDAMeasureUnit(1057, "tablet", ""),
    USDAMeasureUnit(1058, "thigh", ""),
    USDAMeasureUnit(1059, "unit", ""),
    USDAMeasureUnit(1060, "wedge", ""),
    USDAMeasureUnit(1061, "orig ckd g", ""),
    USDAMeasureUnit(1062, "orig rw g", ""),
    USDAMeasureUnit(1063, "medallion", ""),
    USDAMeasureUnit(1064, "pie", ""),
    USDAMeasureUnit(1065, "wing", ""),
    USDAMeasureUnit(1066, "back", ""),
    USDAMeasureUnit(1067, "olive", ""),
    USDAMeasureUnit(1068, "pocket", ""),
    USDAMeasureUnit(1069, "order", ""),
    USDAMeasureUnit(1070, "shrimp", ""),
    USDAMeasureUnit(1071, "each", ""),
    USDAMeasureUnit(1072, "filet", ""),
    USDAMeasureUnit(1073, "plantain", ""),
    USDAMeasureUnit(1074, "nugget", ""),
    USDAMeasureUnit(1075, "pretzel", ""),
    USDAMeasureUnit(1076, "corndog", ""),
    USDAMeasureUnit(1077, "spear", ""),
    USDAMeasureUnit(1078, "sandwich", ""),
    USDAMeasureUnit(1079, "tortilla", ""),
    USDAMeasureUnit(1080, "burrito", ""),
    USDAMeasureUnit(1081, "taco", ""),
    USDAMeasureUnit(1082, "tomatoes", ""),
    USDAMeasureUnit(1083, "chips", ""),
    USDAMeasureUnit(1084, "shell", ""),
    USDAMeasureUnit(1085, "bun", ""),
    USDAMeasureUnit(1086, "crust", ""),
    USDAMeasureUnit(1087, "sheet", ""),
    USDAMeasureUnit(1088, "bag", ""),
    USDAMeasureUnit(1089, "bagel", ""),
    USDAMeasureUnit(1090, "bowl", ""),
    USDAMeasureUnit(1091, "breadstick", ""),
    USDAMeasureUnit(1092, "bulb", ""),
    USDAMeasureUnit(1093, "cake", ""),
    USDAMeasureUnit(1094, "carton", ""),
    USDAMeasureUnit(1095, "chunk", ""),
    USDAMeasureUnit(1096, "contents", ""),
    USDAMeasureUnit(1097, "cutlet", ""),
    USDAMeasureUnit(1098, "doughnut", ""),
    USDAMeasureUnit(1099, "egg", ""),
    USDAMeasureUnit(1100, "fish", ""),
    USDAMeasureUnit(1101, "foreshank", ""),
    USDAMeasureUnit(1102, "frankfurter", ""),
    USDAMeasureUnit(1103, "fries", ""),
    USDAMeasureUnit(1104, "head", ""),
    USDAMeasureUnit(1105, "jar", ""),
    USDAMeasureUnit(1106, "loin", ""),
    USDAMeasureUnit(1107, "pancake", ""),
    USDAMeasureUnit(1108, "pizza", ""),
    USDAMeasureUnit(1109, "rack", ""),
    USDAMeasureUnit(1110, "ribs", ""),
    USDAMeasureUnit(1111, "roll", ""),
    USDAMeasureUnit(1112, "shank", ""),
    USDAMeasureUnit(1113, "shoulder", ""),
    USDAMeasureUnit(1114, "skin", ""),
    USDAMeasureUnit(1115, "wafers", ""),
    USDAMeasureUnit(1116, "wrap", ""),
    USDAMeasureUnit(1117, "bunch", ""),
    USDAMeasureUnit(1118, "tablespoons", ""),
    USDAMeasureUnit(1119, "banana", ""),
    USDAMeasureUnit(1120, "onion", ""),
    USDAMeasureUnit(9999, "undetermined", ""),
]


@dataclasses.dataclass
class USDANutrient:  # pylint: disable=too-many-instance-attributes
    """Wrapper class for USDA Nutrient."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        id_: int,
        name: str,
        unit_name: str,
        nutrient_nbr: str,
        rank: int | None,
        display_name: str,
        description: str | None = None,
        wikipedia_url: str | None = None,
    ) -> None:
        self.id_ = id_
        self.name = name
        self.unit_name = unit_name
        self.nutrient_nbr = nutrient_nbr
        self.rank = rank
        self.display_name = display_name
        self.description = description
        self.wikipedia_url = wikipedia_url


usda_nutrients: list[USDANutrient] = [
    USDANutrient(1001, "Solids", "G", "201", 200, "Solids"),
    USDANutrient(1002, "Nitrogen", "G", "202", 500, "Nitrogen"),
    USDANutrient(
        1003,
        "Protein",
        "G",
        "203",
        600,
        "Protein",
        description="Proteins are essential nutrients for the human body. "
        "They are one of the building blocks of body tissue and can also "
        "serve as a fuel source. As a fuel, proteins provide as much energy "
        "density as carbohydrates: 4 kcal (17 kJ) per gram. Dietary sources "
        "of protein include meats, dairy products, fish, eggs, grains, legumes, "
        "nuts and edible insects.",
        wikipedia_url="https://en.wikipedia.org/wiki/Protein_(nutrient)",
    ),
    USDANutrient(
        1004,
        "Total lipid (fat)",
        "G",
        "204",
        800,
        "Total Fat",
        description="Fats are one of the three main macronutrient groups in "
        "human diet, along with carbohydrates and proteins, and the main "
        "components of common food products like milk, butter, tallow, lard, "
        "salt pork, and cooking oils. They are a major and dense source of food "
        "energy for many animals and play important structural and metabolic "
        "functions, in most living beings, including energy storage, waterproofing, "
        "and thermal insulation. The human body can produce the fat it requires "
        "from other food ingredients, except for a few essential fatty acids that "
        "must be included in the diet.",
        wikipedia_url="https://en.wikipedia.org/wiki/Fat",
    ),
    USDANutrient(
        1005,
        "Carbohydrate, by difference",
        "G",
        "205",
        1110,
        "Total Carbohydrate",
        description="Carbohydrates are central to nutrition and are found in a wide "
        "variety of natural and processed foods. Starch is a polysaccharide. It is "
        "abundant in cereals (wheat, maize, rice), potatoes, and processed food based "
        "on cereal flour, such as bread, pizza or pasta. Sugars appear in human diet "
        "mainly as table sugar (sucrose, extracted from sugarcane or sugar beets), "
        "lactose (abundant in milk), glucose and fructose, both of which occur naturally "
        "in honey, many fruits, and some vegetables. Table sugar, milk, or honey are often "
        "added to drinks and many prepared foods such as jam, biscuits and cakes.",
        wikipedia_url="https://en.wikipedia.org/wiki/Carbohydrate",
    ),
    USDANutrient(1006, "Fiber, crude (DO NOT USE - Archived)", "G", "206", 999999, "Fiber"),
    USDANutrient(1007, "Ash", "G", "207", 1000, "Ash"),
    USDANutrient(
        1008,
        "Energy",
        "KCAL",
        "208",
        300,
        "Calories",
        description="In a nutritional context, the kilojoule (kJ) is the SI unit "
        "of food energy, although the calorie is commonly used. The word calorie "
        "is commonly used with the number of kilocalories (kcal) of nutritional "
        "energy measured. Food nutrients as fat (lipids) contains 9 kilocalories "
        "per gram (kcal/g), while carbohydrate (sugar) or protein contains "
        "approximately 4 kcal/g. Alcohol in food contains 7 kcal/g. Food nutrients "
        'are also often quoted "per 100 g".',
        wikipedia_url="https://en.wikipedia.org/wiki/Calorie#Nutrition",
    ),
    USDANutrient(1009, "Starch", "G", "209", 2200, "Starch"),
    USDANutrient(1010, "Sucrose", "G", "210", 1600, "Sucrose"),
    USDANutrient(1011, "Glucose (dextrose)", "G", "211", 1700, "Glucose (Dextrose)"),
    USDANutrient(1012, "Fructose", "G", "212", 1800, "Fructose"),
    USDANutrient(1013, "Lactose", "G", "213", 1900, "Lactose"),
    USDANutrient(1014, "Maltose", "G", "214", 2000, "Maltose"),
    USDANutrient(1015, "Amylose", "G", "218", 999999, "Amylose"),
    USDANutrient(1016, "Amylopectin", "G", "219", 999999, "Amylopectin"),
    USDANutrient(1017, "Pectin", "G", "220", 999999, "Pectin"),
    USDANutrient(1018, "Alcohol, ethyl", "G", "221", 18200, "Alcohol"),
    USDANutrient(1019, "Pentosan", "G", "222", 999999, "Pentosan"),
    USDANutrient(1020, "Pentoses", "G", "223", 999999, "Pentoses"),
    USDANutrient(1021, "Hemicellulose", "G", "224", 999999, "Hemicellulose"),
    USDANutrient(1022, "Cellulose", "G", "225", 999999, "Cellulose"),
    USDANutrient(1023, "pH", "PH", "226", 999999, "pH (pH)"),
    USDANutrient(1024, "Specific Gravity", "SP_GR", "227", 999999, "Specific Gravity (sp_gr)"),
    USDANutrient(1025, "Organic acids", "G", "229", 2850, "Organic Acids"),
    USDANutrient(1026, "Acetic acid", "MG", "230", 2900, "Acetic Acid"),
    USDANutrient(1027, "Aconitic acid", "MG", "231", 3000, "Aconitic Acid"),
    USDANutrient(1028, "Benzoic acid", "MG", "232", 3100, "Benzoic Acid"),
    USDANutrient(1029, "Chelidonic acid", "MG", "233", 3200, "Chelidonic Acid"),
    USDANutrient(1030, "Chlorogenic acid", "MG", "234", 3300, "Chlorogenic Acid"),
    USDANutrient(1031, "Cinnamic acid", "MG", "235", 3400, "Cinnamic Acid"),
    USDANutrient(1032, "Citric acid", "MG", "236", 3500, "Citric Acid"),
    USDANutrient(1033, "Fumaric acid", "MG", "237", 3600, "Fumaric Acid"),
    USDANutrient(1034, "Galacturonic acid", "MG", "238", 3700, "Galacturonic Acid"),
    USDANutrient(1035, "Gallic acid", "MG", "239", 3800, "Gallic Acid"),
    USDANutrient(1036, "Glycolic acid", "MG", "240", 3900, "Glycolic Acid"),
    USDANutrient(1037, "Isocitric acid", "MG", "241", 4000, "Isocitric Acid"),
    USDANutrient(1038, "Lactic acid", "MG", "242", 4100, "Lactic Acid"),
    USDANutrient(1039, "Malic acid", "MG", "243", 4200, "Malic Acid"),
    USDANutrient(1040, "Oxaloacetic acid", "MG", "244", 4300, "Oxaloacetic Acid"),
    USDANutrient(1041, "Oxalic acid", "MG", "245", 4400, "Oxalic Acid"),
    USDANutrient(1042, "Phytic acid", "MG", "246", 4500, "Phytic Acid"),
    USDANutrient(1043, "Pyruvic acid", "MG", "247", 4600, "Pyruvic Acid"),
    USDANutrient(1044, "Quinic acid", "MG", "248", 4700, "Quinic Acid"),
    USDANutrient(1045, "Salicylic acid", "MG", "249", 4800, "Salicylic Acid"),
    USDANutrient(1046, "Succinic acid", "MG", "250", 4900, "Succinic Acid"),
    USDANutrient(1047, "Tartaric acid", "MG", "251", 5000, "Tartaric Acid"),
    USDANutrient(1048, "Ursolic acid", "MG", "252", 5100, "Ursolic Acid"),
    USDANutrient(1049, "Solids, non-fat", "G", "253", 999999, "Solids, non-fat"),
    USDANutrient(1050, "Carbohydrate, by summation", "G", "205.2", 1120, "Carbohydrate, by summation"),
    USDANutrient(1051, "Water", "G", "255", 100, "Water"),
    USDANutrient(1052, "Adjusted Nitrogen", "G", "256", 999999, "Adjusted Nitrogen"),
    USDANutrient(1053, "Adjusted Protein", "G", "257", 700, "Adjusted Protein"),
    USDANutrient(1054, "Piperine", "G", "259", 999999, "Piperine"),
    USDANutrient(1055, "Mannitol", "G", "260", 2500, "Mannitol"),
    USDANutrient(1056, "Sorbitol", "G", "261", 2600, "Sorbitol"),
    USDANutrient(1057, "Caffeine", "MG", "262", 18300, "Caffeine"),
    USDANutrient(1058, "Theobromine", "MG", "263", 18400, "Theobromine"),
    USDANutrient(1059, "Nitrates", "MG", "264", 999999, "Nitrates"),
    USDANutrient(1060, "Nitrites", "MG", "265", 999999, "Nitrites"),
    USDANutrient(1061, "Nitrosamine,total", "MG", "266", 999999, "Nitrosamine"),
    USDANutrient(1062, "Energy", "kJ", "268", 400, "Energy (kJ)"),
    USDANutrient(1063, "Sugars, Total NLEA", "G", "269.3", 1500, "Total Sugars"),
    USDANutrient(1064, "Solids, soluble", "G", "271", 999999, "Solids, soluble"),
    USDANutrient(1065, "Glycogen", "G", "272", 999999, "Glycogen"),
    USDANutrient(1066, "Fiber, neutral detergent (DO NOT USE - Archived)", "G", "273", 999999, "Fiber"),
    USDANutrient(1067, "Reducing sugars", "G", "274", 999999, "Reducing Sugars"),
    USDANutrient(1068, "Beta-glucans", "G", "276", 999999, "Beta-Glucans"),
    USDANutrient(1069, "Oligosaccharides", "G", "281", 999999, "Oligosaccharides"),
    USDANutrient(1070, "Nonstarch polysaccharides", "G", "282", 999999, "Nonstarch Polysaccharides"),
    USDANutrient(1071, "Resistant starch", "G", "283", 999999, "Resistant Starch"),
    USDANutrient(1072, "Carbohydrate, other", "G", "284", None, "Carbohydrate, other"),
    USDANutrient(1073, "Arabinose", "G", "285", 999999, "Arabinose"),
    USDANutrient(1074, "Xylose", "G", "286", 999999, "Xylose"),
    USDANutrient(1075, "Galactose", "G", "287", 2100, "Galactose"),
    USDANutrient(1076, "Raffinose", "G", "288", 2300, "Raffinose"),
    USDANutrient(1077, "Stachyose", "G", "289", 2400, "Stachyose"),
    USDANutrient(1078, "Xylitol", "G", "290", 2700, "Xylitol"),
    USDANutrient(
        1079,
        "Fiber, total dietary",
        "G",
        "291",
        1200,
        "Dietary Fiber",
        description="Dietary fiber or roughage is the portion of plant-derived "
        "food that cannot be completely broken down by human digestive enzymes. "
        "Dietary fiber has two main components: soluble fiber and insoluble fiber, "
        "which are components of plant foods, such as legumes, whole grains and "
        "cereals, vegetables, fruits, and nuts or seeds. A diet high in regular "
        "fiber consumption is generally associated with supporting health and "
        "lowering the risk of several diseases.",
        wikipedia_url="https://en.wikipedia.org/wiki/Dietary_fiber",
    ),
    USDANutrient(1080, "Lignin", "G", "292", 999999, "Lignin"),
    USDANutrient(1081, "Ribose", "G", "294", 999999, "Ribose"),
    USDANutrient(1082, "Fiber, soluble", "G", "295", 1240, "Soluble Fiber"),
    USDANutrient(1083, "Theophylline", "MG", "296", 999999, "Theophylline"),
    USDANutrient(1084, "Fiber, insoluble", "G", "297", 1260, "Insoluble Fiber"),
    USDANutrient(1085, "Total fat (NLEA)", "G", "298", 900, "Total Fat (NLEA)"),
    USDANutrient(1086, "Total sugar alcohols", "G", "299", 999999, "Sugar Alcohol"),
    USDANutrient(
        1087,
        "Calcium, Ca",
        "MG",
        "301",
        5300,
        "Calcium",
        description="Calcium is a nutrient that all living organisms need, "
        "including humans. It is the most abundant mineral in the body, and "
        "it is vital for bone health. Humans need calcium to build and "
        "maintain strong bones, and 99% of the body’s calcium "
        "is in the bones and teeth. It is also necessary for maintaining "
        "healthy communication between the brain and other parts of the body. "
        "It plays a role in muscle movement and cardiovascular function. "
        "Calcium occurs naturally in many foods, such as yogurt, milk, cheese, "
        "broccoli, tofu, etc. Alongside "
        "calcium, people also need vitamin D, as this vitamin helps the body "
        "absorb calcium. Vitamin D comes from fish oil, fortified dairy products, "
        "and exposure to sunlight.",
        wikipedia_url="https://en.wikipedia.org/wiki/Calcium_in_biology",
    ),
    USDANutrient(1088, "Chlorine, Cl", "MG", "302", 999999, "Chlorine"),
    USDANutrient(
        1089,
        "Iron, Fe",
        "MG",
        "303",
        5400,
        "Iron",
        description="Iron is pervasive, but particularly rich sources of dietary "
        "iron include red meat, oysters, lentils, beans, poultry, fish, leaf vegetables, "
        "watercress, tofu, chickpeas, black-eyed peas, and blackstrap molasses. Bread "
        "and breakfast cereals are sometimes specifically fortified with iron.",
        wikipedia_url="https://en.wikipedia.org/wiki/Iron#Nutrition",
    ),
    USDANutrient(
        1090,
        "Magnesium, Mg",
        "MG",
        "304",
        5500,
        "Magnesium",
        description="The important interaction between phosphate and magnesium ions "
        "makes magnesium essential to the basic nucleic acid chemistry of all cells "
        "of all known living organisms. More than 300 enzymes require magnesium ions "
        "for their catalytic action, including all enzymes using or synthesizing ATP "
        "and those that use other nucleotides to synthesize DNA and RNA. Spices, nuts, "
        "cereals, cocoa and vegetables are rich sources of magnesium. Green leafy "
        "vegetables such as spinach are also rich in magnesium. Beverages rich in "
        "magnesium are coffee, tea, and cocoa.",
        wikipedia_url="https://en.wikipedia.org/wiki/Magnesium#Biological_roles",
    ),
    USDANutrient(
        1091,
        "Phosphorus, P",
        "MG",
        "305",
        5600,
        "Phosphorus",
        description="Phosphorus plays a major role in the structural framework of DNA and RNA. "
        "Living cells use phosphate to transport cellular energy with adenosine triphosphate (ATP), "
        "necessary for every cellular process that uses energy. The main food sources for phosphorus "
        "are the same as those "
        "containing protein, although proteins do not contain phosphorus. For "
        "example, milk, meat, and soya typically also have phosphorus. As a "
        "rule, if a diet has sufficient protein and calcium, the amount of "
        "phosphorus is probably sufficient.",
        wikipedia_url="https://en.wikipedia.org/wiki/Phosphorus#Biological_role",
    ),
    USDANutrient(
        1092,
        "Potassium, K",
        "MG",
        "306",
        5700,
        "Potassium",
        description="Eating a variety of foods that contain potassium is "
        "the best way to get an adequate amount. Foods with high sources "
        "of potassium include kiwifruit, orange juice, potatoes, bananas, "
        "coconut, avocados, apricots, parsnips and turnips, although many "
        "other fruits, vegetables, legumes, and meats contain potassium. "
        "Common foods very high in potassium are beans (white beans and others), "
        "dark leafy greens (spinach, Swiss chard, and others), baked potatoes, "
        "dried fruit (apricots, peaches, prunes, raisins; figs and dates), baked "
        "squash, yogurt, fish (salmon), avocado, and banana; "
        "nuts (pistachios, almonds, walnuts, etc.) and seeds (squash, pumpkin, sunflower)",
        wikipedia_url="https://en.wikipedia.org/wiki/Potassium_in_biology#Dietary_recommendations",
    ),
    USDANutrient(
        1093,
        "Sodium, Na",
        "MG",
        "307",
        5800,
        "Sodium",
        description="Sodium is an essential nutrient for human health "
        "via its role as an electrolyte and osmotic solute. Excessive "
        "salt consumption may increase the risk of cardiovascular diseases, "
        "such as hypertension, in children and adults. "
        "Accordingly, numerous world health "
        "associations and experts in developed countries recommend reducing "
        "consumption of popular salty foods.",
        wikipedia_url="https://en.wikipedia.org/wiki/Salt",
    ),
    USDANutrient(1094, "Sulfur, S", "MG", "308", 6241, "Sulfur"),
    USDANutrient(
        1095,
        "Zinc, Zn",
        "MG",
        "309",
        5900,
        "Zinc",
        description="Zinc is an essential trace element for humans. Zinc is "
        "required for the function of over 300 enzymes and 1000 transcription "
        "factors, and is stored and transferred in metallothioneins. It is the "
        "second most abundant trace metal in humans after iron and it is the only "
        "metal which appears in all enzyme classes. Animal products such as meat, "
        "fish, shellfish, fowl, eggs, and dairy contain zinc. The concentration of "
        "zinc in plants varies with the level in the soil. With adequate zinc in the "
        "soil, the food plants that contain the most zinc are wheat (germ and bran) and "
        "various seeds, including sesame, poppy, alfalfa, celery, and mustard. Zinc is "
        "also found in beans, nuts, almonds, whole grains, pumpkin seeds, sunflower "
        "seeds, and blackcurrant.",
        wikipedia_url="https://en.wikipedia.org/wiki/Zinc#Nutrition",
    ),
    USDANutrient(1096, "Chromium, Cr", "UG", "310", 999999, "Chromium"),
    USDANutrient(1097, "Cobalt, Co", "UG", "311", 6244, "Cobalt"),
    USDANutrient(
        1098,
        "Copper, Cu",
        "MG",
        "312",
        6000,
        "Copper",
        description="Copper is an essential trace element in plants and animals. "
        "Copper is absorbed in the gut, then transported to the liver bound to albumin. "
        "After processing in the liver, copper is distributed to other tissues in a "
        "second phase. Copper proteins have diverse roles in biological electron "
        "transport and oxygen transportation, and essential in the aerobic respiration. "
        "Rich sources of copper include oysters, beef and lamb liver, Brazil nuts, "
        "blackstrap molasses, cocoa, and black pepper. Good sources include lobster, "
        "nuts and sunflower seeds, green olives, avocados, and wheat bran.",
        wikipedia_url="https://en.wikipedia.org/wiki/Copper#Nutrition",
    ),
    USDANutrient(1099, "Fluoride, F", "UG", "313", 6240, "Fluoride"),
    USDANutrient(
        1100,
        "Iodine, I",
        "UG",
        "314",
        6150,
        "Iodine",
        description="Iodine is an essential element for life. It is required "
        "for the synthesis of the growth-regulating thyroid hormones thyroxine "
        "and triiodothyronine. Natural sources of dietary iodine include seafood, "
        "such as fish, seaweeds (such as kelp) and shellfish, dairy products and "
        "eggs so long as the animals received enough iodine, and plants grown on "
        "iodine-rich soil. Iodised salt is fortified with iodine in the form of sodium iodide.",
        wikipedia_url="https://en.wikipedia.org/wiki/Iodine",
    ),
    USDANutrient(
        1101,
        "Manganese, Mn",
        "MG",
        "315",
        6100,
        "Manganese",
        description="Manganese is an essential human dietary element. "
        "It is present as a coenzyme in several biological processes, "
        "which include macronutrient metabolism, bone formation, and "
        "free radical defense systems. It is a critical component in "
        "dozens of proteins and enzymes.",
        wikipedia_url="https://en.wikipedia.org/wiki/Manganese#Biological_role_in_humans",
    ),
    USDANutrient(1102, "Molybdenum, Mo", "UG", "316", 6243, "Molybdenum"),
    USDANutrient(
        1103,
        "Selenium, Se",
        "UG",
        "317",
        6200,
        "Selenium",
        description="Although it is toxic in large doses, selenium is an essential "
        "micronutrient for animals. Dietary selenium comes from meat, nuts, cereals "
        "and mushrooms. Brazil nuts are the richest dietary source.",
        wikipedia_url="https://en.wikipedia.org/wiki/Selenium#Biological_role",
    ),
    USDANutrient(1104, "Vitamin A, IU", "IU", "318", 7500, "Vitamin A"),
    USDANutrient(1105, "Retinol", "UG", "319", 7430, "Retinol"),
    USDANutrient(
        1106,
        "Vitamin A, RAE",
        "UG",
        "320",
        7420,
        "Vitamin A",
        description="Vitamin A is a group of unsaturated nutritional "
        "organic compounds that includes retinol, retinal, and several "
        "provitamin A carotenoids (most notably beta-carotene). Vitamin A "
        "has multiple functions: it is important for growth and development, "
        "for the maintenance of the immune system, and for good vision. "
        "Vitamin A is found in many foods, including cod liver oil, liver turkey, carrot, "
        "broccoli, butter, kale, etc.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_A",
    ),
    USDANutrient(1107, "Carotene, beta", "UG", "321", 7440, "Beta Carotene"),
    USDANutrient(1108, "Carotene, alpha", "UG", "322", 7450, "Alpha Carotene"),
    USDANutrient(
        1109,
        "Vitamin E (alpha-tocopherol)",
        "MG",
        "323",
        7905,
        "Vitamin E",
        description="Vitamin E is a group of eight fat soluble compounds that "
        "include four tocopherols and four tocotrienols. Vitamin E deficiency, "
        "which is rare and usually due to an underlying problem with digesting "
        "dietary fat rather than from a diet low in vitamin E, can cause nerve problems. "
        "Vitamin E is a fat-soluble antioxidant which may help protect cell membranes from "
        "reactive oxygen species.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_E",
    ),
    USDANutrient(1110, "Vitamin D (D2 + D3), International Units", "IU", "324", 8650, "Vitamin D"),
    USDANutrient(1111, "Vitamin D2 (ergocalciferol)", "UG", "325", 8710, "Vitamin D2 (ergocalciferol)"),
    USDANutrient(1112, "Vitamin D3 (cholecalciferol)", "UG", "326", 8720, "Vitamin D3 (cholecalciferol)"),
    USDANutrient(1113, "25-hydroxycholecalciferol", "UG", "327", 8730, "25-Hydroxycholecalciferol"),
    USDANutrient(
        1114,
        "Vitamin D (D2 + D3)",
        "UG",
        "328",
        8700,
        "Vitamin D",
        description="Vitamin D (also referred to as “calciferol”) is a fat-soluble vitamin "
        "that is naturally present in a few foods, added to others, and available as a "
        "dietary supplement. It is also produced endogenously when ultraviolet (UV) rays "
        "from sunlight strike the skin and trigger vitamin D synthesis. "
        "Few foods naturally contain vitamin D. The flesh of fatty fish (such as trout, "
        "salmon, tuna, and mackerel) and fish liver oils are among the best sources. "
        "Beef liver, egg yolks, and cheese have small amounts of vitamin D.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_D",
    ),
    USDANutrient(1115, "25-hydroxyergocalciferol", "UG", "329", 8740, "25-Hydroxyergocalciferol"),
    USDANutrient(1116, "Phytoene", "UG", "330", 7570, "Phytoene"),
    USDANutrient(1117, "Phytofluene", "UG", "331", 7580, "Phytofluene"),
    USDANutrient(1118, "Carotene, gamma", "UG", "332", 7455, "Gamma Carotene"),
    USDANutrient(1119, "Zeaxanthin", "UG", "338.2", 7564, "Zeaxanthin"),
    USDANutrient(1120, "Cryptoxanthin, beta", "UG", "334", 7460, "Beta Cryptoxanthin"),
    USDANutrient(1121, "Lutein", "UG", "338.1", 7562, "Lutein"),
    USDANutrient(1122, "Lycopene", "UG", "337", 7530, "Lycopene"),
    USDANutrient(1123, "Lutein + zeaxanthin", "UG", "338", 7560, "Lutein + Zeaxanthin"),
    USDANutrient(1124, "Vitamin E (label entry primarily)", "IU", "340", 999999, "Vitamin E (Label Entry Primarily)"),
    USDANutrient(1125, "Tocopherol, beta", "MG", "341", 8000, "Beta Tocopherol"),
    USDANutrient(1126, "Tocopherol, gamma", "MG", "342", 8100, "Gamma Tocopherol"),
    USDANutrient(1127, "Tocopherol, delta", "MG", "343", 8200, "Delta Tocopherol"),
    USDANutrient(1128, "Tocotrienol, alpha", "MG", "344", 8300, "Alpha Tocotrienol"),
    USDANutrient(1129, "Tocotrienol, beta", "MG", "345", 8400, "Beta Tocotrienol"),
    USDANutrient(1130, "Tocotrienol, gamma", "MG", "346", 8500, "Gamma Tocotrienol"),
    USDANutrient(1131, "Tocotrienol, delta", "MG", "347", 8600, "Delta Tocotrienol"),
    USDANutrient(1132, "Aluminum, Al", "UG", "348", 999999, "Aluminum"),
    USDANutrient(1133, "Antimony, Sb", "UG", "349", 999999, "Antimony"),
    USDANutrient(1134, "Arsenic, As", "UG", "350", 999999, "Arsenic"),
    USDANutrient(1135, "Barium, Ba", "UG", "351", 999999, "Barium"),
    USDANutrient(1136, "Beryllium, Be", "UG", "352", 999999, "Beryllium"),
    USDANutrient(1137, "Boron, B", "UG", "354", 6245, "Boron"),
    USDANutrient(1138, "Bromine, Br", "UG", "355", 999999, "Bromine"),
    USDANutrient(1139, "Cadmium, Cd", "UG", "356", 999999, "Cadmium"),
    USDANutrient(1140, "Gold, Au", "UG", "363", 999999, "Gold"),
    USDANutrient(1141, "Iron, heme", "MG", "364", 999999, "Iron, heme"),
    USDANutrient(1142, "Iron, non-heme", "MG", "365", 999999, "Iron, non-heme"),
    USDANutrient(1143, "Lead, Pb", "UG", "367", 999999, "Lead"),
    USDANutrient(1144, "Lithium, Li", "UG", "368", 999999, "Lithium"),
    USDANutrient(1145, "Mercury, Hg", "UG", "370", 999999, "Mercury"),
    USDANutrient(1146, "Nickel, Ni", "UG", "371", 6242, "Nickel"),
    USDANutrient(1147, "Rubidium, Rb", "UG", "373", 999999, "Rubidium"),
    USDANutrient(1148, "Fluoride - DO NOT USE; use 313", "UG", "374", 6250, "Fluoride"),
    USDANutrient(1149, "Salt, NaCl", "MG", "375", 999999, "Salt"),
    USDANutrient(1150, "Silicon, Si", "UG", "378", 999999, "Silicon"),
    USDANutrient(1151, "Silver, Ag", "UG", "379", 999999, "Silver"),
    USDANutrient(1152, "Strontium, Sr", "UG", "380", 999999, "Strontium"),
    USDANutrient(1153, "Tin, Sn", "UG", "385", 999999, "Tin"),
    USDANutrient(1154, "Titanium, Ti", "UG", "386", 999999, "Titanium"),
    USDANutrient(1155, "Vanadium, V", "UG", "389", 999999, "Vanadium"),
    USDANutrient(1156, "Vitamin A, RE", "MCG_RE", "392", 7500, "Vitamin A (mcg_re)"),
    USDANutrient(1157, "Carotene", "MCG_RE", "393", 7600, "Carotene (mcg_re)"),
    USDANutrient(1158, "Vitamin E", "MG_ATE", "394", 7800, "Vitamin E (mg_ate)"),
    USDANutrient(1159, "cis-beta-Carotene", "UG", "321.1", 7442, "Cis-Beta-Carotene"),
    USDANutrient(1160, "cis-Lycopene", "UG", "337.1", 7532, "Cis-Lycopene"),
    USDANutrient(1161, "cis-Lutein/Zeaxanthin", "UG", "338.3", 7561, "Cis-Lutein/Zeaxanthin"),
    USDANutrient(
        1162,
        "Vitamin C, total ascorbic acid",
        "MG",
        "401",
        6300,
        "Vitamin C",
        description="Vitamin C (also known as ascorbic acid and ascorbate) is a vitamin "
        "found in various foods and sold as a dietary supplement. It is used to prevent "
        "and treat scurvy. Vitamin C is an essential nutrient involved in the repair of "
        "tissue, the formation of collagen, and the enzymatic production of certain "
        "neurotransmitters. It is required for the functioning of several enzymes and "
        "is important for immune system function. It also functions as an antioxidant.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_C",
    ),
    USDANutrient(1163, "Vitamin C, reduced ascorbic acid", "MG", "402", 999999, "Vitamin C, reduced ascorbic acid"),
    USDANutrient(1164, "Vitamin C, dehydro ascorbic acid", "MG", "403", 999999, "Vitamin C, dehyrdo ascorbic acid"),
    USDANutrient(
        1165,
        "Thiamin",
        "MG",
        "404",
        6400,
        "Thiamin",
        description="Thiamine, also known as thiamin or vitamin B1, is a vitamin found "
        "in food and manufactured as a dietary supplement and medication. Food sources "
        "of thiamine include whole grains, legumes, and some meats and fish. Grain "
        "processing removes much of the thiamine content, so in many countries cereals "
        "and flours are enriched with thiamine. Supplements and medications are available "
        "to treat and prevent thiamine deficiency and disorders that result from it, "
        "including beriberi and Wernicke encephalopathy.",
        wikipedia_url="https://en.wikipedia.org/wiki/Thiamine",
    ),
    USDANutrient(
        1166,
        "Riboflavin",
        "MG",
        "405",
        6500,
        "Riboflavin",
        description="Riboflavin, also known as vitamin B2, is a vitamin found in food "
        "and consumed as a dietary supplement. Food sources include beef liver, whey protein, "
        "eggs, beef, fish, chicken, almonds, peanuts, cheese, etc. The milling of cereals results "
        "in considerable loss (up to 60%) of riboflavin, so white flour is enriched in some "
        "countries. Riboflavin is added to baby foods, breakfast cereals, pastas and "
        "vitamin-enriched meal replacement products",
        wikipedia_url="https://en.wikipedia.org/wiki/Riboflavin",
    ),
    USDANutrient(
        1167,
        "Niacin",
        "MG",
        "406",
        6600,
        "Niacin",
        description="Niacin, also known as nicotinic acid, is an organic compound and "
        "a form of vitamin B3, an essential human nutrient. Niacin is obtained in the "
        "diet from a variety of whole and processed foods, with highest contents in "
        "fortified packaged foods, meat, poultry, red fish such as tuna and salmon, "
        "lesser amounts in nuts, legumes and seeds.",
        wikipedia_url="https://en.wikipedia.org/wiki/Niacin",
    ),
    USDANutrient(
        1168, "Niacin from tryptophan, determined", "MG", "407", 999999, "Niacin From Tryptophan, determined"
    ),
    USDANutrient(1169, "Niacin equivalent N406 +N407", "MG", "409", 999999, "Niacin Equivalent N406 +N407"),
    USDANutrient(
        1170,
        "Pantothenic acid",
        "MG",
        "410",
        6700,
        "Pantothenic Acid",
        description="Pantothenic acid, also called vitamin B5 is a water-soluble B "
        "vitamin and therefore an essential nutrient. All animals require pantothenic "
        "acid in order to synthesize coenzyme A (CoA) – essential for fatty acid "
        "metabolism – as well as to, in general, synthesize and metabolize proteins, "
        "carbohydrates, and fats.",
        wikipedia_url="https://en.wikipedia.org/wiki/Pantothenic_acid",
    ),
    USDANutrient(
        1171, "Vitamin B-6, pyridoxine, alcohol form", "MG", "411", 999999, "Vitamin B-6, pyridoxine, alcohol form"
    ),
    USDANutrient(
        1172, "Vitamin B-6, pyridoxal, aldehyde form", "MG", "412", 999999, "Vitamin B-6, pyridoxal, aldehyde form"
    ),
    USDANutrient(
        1173, "Vitamin B-6, pyridoxamine, amine form", "MG", "413", 999999, "Vitamin B-6, pyridoxamine, amine form"
    ),
    USDANutrient(1174, "Vitamin B-6, N411 + N412 +N413", "MG", "414", 999999, "Vitamin B-6, N411 + N412 +N413"),
    USDANutrient(
        1175,
        "Vitamin B-6",
        "MG",
        "415",
        6800,
        "Vitamin B6",
        description="Vitamin B6 is one of the B vitamins, and thus an essential nutrient. "
        "Beef, pork, fowl and fish are generally good sources; dairy, eggs, mollusks and "
        "crustaceans also contain vitamin B6, but at lower levels. There is enough in a "
        "wide variety of plant foods so that a vegetarian or vegan diet does not put "
        "consumers at risk for deficiency.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_B6",
    ),
    USDANutrient(1176, "Biotin", "UG", "416", 6850, "Biotin"),
    USDANutrient(
        1177,
        "Folate, total",
        "UG",
        "417",
        6900,
        "Folate DFE",
        description="Folate, also known as vitamin B9 and folacin, is one of the B vitamins. "
        "Manufactured folic acid, which is converted into folate by the body, is used as a "
        "dietary supplement and in food fortification as it is more stable during processing "
        "and storage. Folate is required for the body to make DNA and RNA and metabolise "
        "amino acids necessary for cell division. As humans cannot make folate, it is "
        "required in the diet, making it an essential nutrient. It occurs naturally in many "
        "foods such as peanuts, sunflower seeds, lentils, chickpeas, asparagus, spinach, etc.",
        wikipedia_url="https://en.wikipedia.org/wiki/Folate",
    ),
    USDANutrient(
        1178,
        "Vitamin B-12",
        "UG",
        "418",
        7300,
        "Vitamin B12",
        description="Vitamin B12, also known as cobalamin, is a water-soluble vitamin "
        "involved in metabolism. It is one of eight B vitamins. It is a cofactor in DNA "
        "synthesis, in both fatty acid and amino acid metabolism. It is important in the "
        "normal functioning of the nervous system via its role in the synthesis of myelin, "
        "and in the maturation of red blood cells in the bone marrow. Meat, liver, eggs and "
        "milk are good sources of the vitamin.",
        wikipedia_url="https://en.wikipedia.org/wiki/Vitamin_B12",
    ),
    USDANutrient(1179, "Folate, free", "UG", "419", 999999, "Folate, free"),
    USDANutrient(
        1180,
        "Choline, total",
        "MG",
        "421",
        7220,
        "Choline",
        description="Choline is an essential nutrient for humans and many other animals. "
        "Symptomatic choline deficiency is rare in humans. Most obtain sufficient amounts "
        "of it from the diet and are able to biosynthesize limited amounts of it. Eggs, Bacon, beef, "
        "cod, broccoli, brussel sprouts, carrots, butter, cheese are good sources of Choline. ",
        wikipedia_url="https://en.wikipedia.org/wiki/Choline",
    ),
    USDANutrient(1181, "Inositol", "MG", "422", 2800, "Inositol"),
    USDANutrient(1182, "Inositol phosphate", "MG", "423", 999999, "Inositol Phosphate"),
    USDANutrient(1183, "Vitamin K (Menaquinone-4)", "UG", "428", 8950, "Vitamin K"),
    USDANutrient(1184, "Vitamin K (Dihydrophylloquinone)", "UG", "429", 8900, "Vitamin K (Dihydrophylloquinone)"),
    USDANutrient(1185, "Vitamin K (phylloquinone)", "UG", "430", 8800, "Vitamin K (Phylloquinone)"),
    USDANutrient(1186, "Folic acid", "UG", "431", 7000, "Folic Acid"),
    USDANutrient(1187, "Folate, food", "UG", "432", 7100, "Folate, food"),
    USDANutrient(
        1188, "5-methyl tetrahydrofolate (5-MTHF)", "UG", "433", 999999, "5-Methyl Tetrahydrofolate (5-MTHF)"
    ),
    USDANutrient(1189, "Folate, not 5-MTHF", "UG", "434", 999999, "Folate, not 5-MTHF"),
    USDANutrient(1190, "Folate, DFE", "UG", "435", 7200, "Folate, DFE"),
    USDANutrient(1191, "10-Formyl folic acid (10HCOFA)", "UG", "436", 999999, "10-Formyl Folic Acid (10HCOFA)"),
    USDANutrient(
        1192, "5-Formyltetrahydrofolic acid (5-HCOH4)", "UG", "437", 999999, "5-Formyltetrahydrofolic Acid (5-HCOH4)"
    ),
    USDANutrient(1193, "Tetrahydrofolic acid (THF)", "UG", "438", 999999, "Tetrahydrofolic Acid (THF)"),
    USDANutrient(1194, "Choline, free", "MG", "450", 7230, "Choline, free"),
    USDANutrient(1195, "Choline, from phosphocholine", "MG", "451", 7240, "Choline, from phosphocholine"),
    USDANutrient(1196, "Choline, from phosphotidyl choline", "MG", "452", 7250, "Choline, from phosphotidyl choline"),
    USDANutrient(
        1197, "Choline, from glycerophosphocholine", "MG", "453", 7260, "Choline, from glycerophosphocholine"
    ),
    USDANutrient(1198, "Betaine", "MG", "454", 7290, "Betaine"),
    USDANutrient(1199, "Choline, from sphingomyelin", "MG", "455", 7270, "Choline, from sphingomyelin"),
    USDANutrient(1200, "p-Hydroxy benzoic acid", "MG", "460", 999999, "p-Hydroxy Benzoic Acid"),
    USDANutrient(1201, "Caffeic acid", "MG", "461", 999999, "Caffeic Acid"),
    USDANutrient(1202, "p-Coumaric acid", "MG", "462", 999999, "p-Coumaric Acid"),
    USDANutrient(1203, "Ellagic acid", "MG", "463", 999999, "Ellagic Acid"),
    USDANutrient(1204, "Ferrulic acid", "MG", "464", 999999, "Ferrulic Acid"),
    USDANutrient(1205, "Gentisic acid", "MG", "465", 999999, "Gentisic Acid"),
    USDANutrient(1206, "Tyrosol", "MG", "466", 999999, "Tyrosol"),
    USDANutrient(1207, "Vanillic acid", "MG", "467", 999999, "Vanillic Acid"),
    USDANutrient(1208, "Phenolic acids, total", "MG", "469", 999999, "Total Phenolic Acids"),
    USDANutrient(1209, "Polyphenols, total", "MG", "470", 999999, "Total Polyphenols"),
    USDANutrient(1210, "Tryptophan", "G", "501", 16300, "Tryptophan"),
    USDANutrient(1211, "Threonine", "G", "502", 16400, "Threonine"),
    USDANutrient(1212, "Isoleucine", "G", "503", 16500, "Isoleucine"),
    USDANutrient(1213, "Leucine", "G", "504", 16600, "Leucine"),
    USDANutrient(1214, "Lysine", "G", "505", 16700, "Lysine"),
    USDANutrient(1215, "Methionine", "G", "506", 16800, "Methionine"),
    USDANutrient(1216, "Cystine", "G", "507", 16900, "Cystine"),
    USDANutrient(1217, "Phenylalanine", "G", "508", 17000, "Phenylalanine"),
    USDANutrient(1218, "Tyrosine", "G", "509", 17100, "Tyrosine"),
    USDANutrient(1219, "Valine", "G", "510", 17200, "Valine"),
    USDANutrient(1220, "Arginine", "G", "511", 17300, "Arginine"),
    USDANutrient(1221, "Histidine", "G", "512", 17400, "Histidine"),
    USDANutrient(1222, "Alanine", "G", "513", 17500, "Alanine"),
    USDANutrient(1223, "Aspartic acid", "G", "514", 17600, "Aspartic Acid"),
    USDANutrient(1224, "Glutamic acid", "G", "515", 17700, "Glutamic Acid"),
    USDANutrient(1225, "Glycine", "G", "516", 17800, "Glycine"),
    USDANutrient(1226, "Proline", "G", "517", 17900, "Proline"),
    USDANutrient(1227, "Serine", "G", "518", 18000, "Serine"),
    USDANutrient(1228, "Hydroxyproline", "G", "521", 18100, "Hydroxyproline"),
    USDANutrient(
        1229,
        "Cysteine and methionine(sulfer containing AA)",
        "G",
        "522",
        999999,
        "Cysteine and Methionine(Sulfer containing AA)",
    ),
    USDANutrient(
        1230,
        "Phenylalanine and tyrosine (aromatic  AA)",
        "G",
        "523",
        999999,
        "Phenylalanine and Tyrosine (Aromatic  AA)",
    ),
    USDANutrient(1231, "Asparagine", "G", "525", 999999, "Asparagine"),
    USDANutrient(1232, "Cysteine", "G", "526", 18150, "Cysteine"),
    USDANutrient(1233, "Glutamine", "G", "528", 999999, "Glutamine"),
    USDANutrient(1234, "Taurine", "G", "529", 999999, "Taurine"),
    USDANutrient(
        1235,
        "Sugars, added",
        "G",
        "539",
        1540,
        "Added Sugars",
        description="Added sugars are sugar carbohydrates (caloric sweeteners) "
        "added to food and beverages during their production (industrial processing). "
        "This type of sugar is chemically indistinguishable from naturally occurring "
        'sugars, but the term "added sugar" is used to identify sweetened foods.',
        wikipedia_url="https://en.wikipedia.org/wiki/Added_sugar",
    ),
    USDANutrient(1236, "Sugars, intrinsic", "G", "549", 1520, "Sugars, intrinsic"),
    USDANutrient(1237, "Calcium, added", "MG", "551", 5340, "Calcium, added"),
    USDANutrient(1238, "Iron, added", "MG", "553", 5440, "Iron, added"),
    USDANutrient(1239, "Calcium, intrinsic", "MG", "561", 5320, "Calcium, intrinsic"),
    USDANutrient(1240, "Iron, intrinsic", "MG", "563", 5420, "Iron, intrinsic"),
    USDANutrient(1241, "Vitamin C, added", "MG", "571", 6340, "Vitamin C, added"),
    USDANutrient(1242, "Vitamin E, added", "MG", "573", 7920, "Vitamin E, added"),
    USDANutrient(1243, "Thiamin, added", "MG", "574", 6440, "Thiamin, added"),
    USDANutrient(1244, "Riboflavin, added", "MG", "575", 6540, "Riboflavin, added"),
    USDANutrient(1245, "Niacin, added", "MG", "576", 6640, "Niacin, added"),
    USDANutrient(1246, "Vitamin B-12, added", "UG", "578", 7340, "Vitamin B-12, added"),
    USDANutrient(1247, "Vitamin C, intrinsic", "MG", "581", 6320, "Vitamin C, intrinsic"),
    USDANutrient(1248, "Vitamin E, intrinsic", "MG", "583", 7930, "Vitamin E, intrinsic"),
    USDANutrient(1249, "Thiamin, intrinsic", "MG", "584", 6420, "Thiamin, intrinsic"),
    USDANutrient(1250, "Riboflavin, intrinsic", "MG", "585", 6520, "Riboflavin, intrinsic"),
    USDANutrient(1251, "Niacin, intrinsic", "MG", "586", 6620, "Niacin, intrinsic"),
    USDANutrient(1252, "Vitamin B-12, intrinsic", "UG", "588", 7320, "Vitamin B-12, intrinsic"),
    USDANutrient(
        1253,
        "Cholesterol",
        "MG",
        "601",
        15700,
        "Cholesterol",
        description="Animal fats are complex mixtures of triglycerides, with "
        "lesser amounts of both the phospholipids and cholesterol molecules from "
        "which all animal (and human) cell membranes are constructed. Since "
        "all animal cells manufacture cholesterol, all animal-based foods contain "
        "cholesterol in varying amounts. Major dietary sources of cholesterol "
        "include red meat, egg yolks and whole eggs, liver, kidney, giblets, fish oil, "
        "and butter. Human breast milk also contains significant quantities of cholesterol.",
        wikipedia_url="https://en.wikipedia.org/wiki/Cholesterol",
    ),
    USDANutrient(1254, "Glycerides", "G", "602", 999999, "Glycerides"),
    USDANutrient(1255, "Phospholipids", "G", "603", 999999, "Phospholipids"),
    USDANutrient(1256, "Glycolipids", "G", "604", 999999, "Glycolipids"),
    USDANutrient(1257, "Fatty acids, total trans", "G", "605", 15400, "Trans Fat"),
    USDANutrient(
        1258,
        "Fatty acids, total saturated",
        "G",
        "606",
        9700,
        "Saturated Fat",
        description="Most animal fats are saturated. The fats of plants and fish "
        "are generally unsaturated. Various foods contain different proportions "
        "of saturated and unsaturated fat. Many processed foods like foods deep-fried "
        "in hydrogenated oil and sausage are high in saturated fat content. Some "
        "store-bought baked goods are as well, especially those containing partially "
        "hydrogenated oils. Other examples of foods containing a high proportion of "
        "saturated fat and dietary cholesterol include animal fat products such as lard "
        "or schmaltz, fatty meats and dairy products made with whole or reduced fat "
        "milk like yogurt, ice cream, cheese and butter. Certain vegetable products "
        "have high saturated fat content, such as coconut oil and palm kernel oil.",
        wikipedia_url="https://en.wikipedia.org/wiki/Saturated_fat",
    ),
    USDANutrient(1259, "SFA 4:0", "G", "607", 9800, "SFA 4:0"),
    USDANutrient(1260, "SFA 6:0", "G", "608", 9900, "SFA 6:0"),
    USDANutrient(1261, "SFA 8:0", "G", "609", 10000, "SFA 8:0"),
    USDANutrient(1262, "SFA 10:0", "G", "610", 10100, "SFA 10:0"),
    USDANutrient(1263, "SFA 12:0", "G", "611", 10300, "SFA 12:0"),
    USDANutrient(1264, "SFA 14:0", "G", "612", 10500, "SFA 14:0"),
    USDANutrient(1265, "SFA 16:0", "G", "613", 10700, "SFA 16:0"),
    USDANutrient(1266, "SFA 18:0", "G", "614", 10900, "SFA 18:0"),
    USDANutrient(1267, "SFA 20:0", "G", "615", 11100, "SFA 20:0"),
    USDANutrient(1268, "MUFA 18:1", "G", "617", 12100, "MUFA 18:1"),
    USDANutrient(1269, "PUFA 18:2", "G", "618", 13100, "PUFA 18:2"),
    USDANutrient(1270, "PUFA 18:3", "G", "619", 13900, "PUFA 18:3"),
    USDANutrient(1271, "PUFA 20:4", "G", "620", 14700, "PUFA 20:4"),
    USDANutrient(1272, "PUFA 22:6 n-3 (DHA)", "G", "621", 15300, "Omega-3 (DHA)"),
    USDANutrient(1273, "SFA 22:0", "G", "624", 11200, "SFA 22:0"),
    USDANutrient(1274, "MUFA 14:1", "G", "625", 11500, "MUFA 14:1"),
    USDANutrient(1275, "MUFA 16:1", "G", "626", 11700, "MUFA 16:1"),
    USDANutrient(1276, "PUFA 18:4", "G", "627", 14250, "PUFA 18:4"),
    USDANutrient(1277, "MUFA 20:1", "G", "628", 12400, "MUFA 20:1"),
    USDANutrient(1278, "PUFA 2:5 n-3 (EPA)", "G", "629", 15000, "Omega-3 (EPA)"),
    USDANutrient(1279, "MUFA 22:1", "G", "630", 12500, "MUFA 22:1"),
    USDANutrient(1280, "PUFA 22:5 n-3 (DPA)", "G", "631", 15200, "Omega-3 (DPA)"),
    USDANutrient(1281, "TFA 14:1 t", "G", "821", 15510, "TFA 14:1 t"),
    USDANutrient(1283, "Phytosterols", "MG", "636", 15800, "Phytosterols"),
    USDANutrient(1284, "Ergosterol", "MG", "637", 16220, "Ergosterol"),
    USDANutrient(1285, "Stigmasterol", "MG", "638", 15900, "Stigmasterol"),
    USDANutrient(1286, "Campesterol", "MG", "639", 16000, "Campesterol"),
    USDANutrient(1287, "Brassicasterol", "MG", "640", 16100, "Brassicasterol"),
    USDANutrient(1288, "Beta-sitosterol", "MG", "641", 16200, "Beta-Sitosterol"),
    USDANutrient(1289, "Campestanol", "MG", "642", 16221, "Campestanol"),
    USDANutrient(1290, "Unsaponifiable matter (lipids)", "G", "643", 999999, "Unsaponifiable Matter (Lipids)"),
    USDANutrient(
        1291,
        "Fatty acids, other than 607-615, 617-621, 624-632, 652-654, 686-689)",
        "G",
        "644",
        999999,
        "Fatty Acids, other than 607-615, 617-621, 624-632, 652-654, 686-689)",
    ),
    USDANutrient(1292, "Fatty acids, total monounsaturated", "G", "645", 11400, "Monounsaturated Fat"),
    USDANutrient(1293, "Fatty acids, total polyunsaturated", "G", "646", 12900, "Polyunsaturated Fat"),
    USDANutrient(1294, "Beta-sitostanol", "MG", "647", 16222, "Beta-Sitostanol"),
    USDANutrient(1295, "Delta-7-avenasterol", "MG", "648", 16223, "Delta-7-Avenasterol"),
    USDANutrient(1296, "Delta-5-avenasterol", "MG", "649", 16224, "Delta-5-Avenasterol"),
    USDANutrient(1297, "Alpha-spinasterol", "MG", "650", 16225, "Alpha-Spinasterol"),
    USDANutrient(1298, "Phytosterols, other", "MG", "651", 16227, "Phytosterols, other"),
    USDANutrient(1299, "SFA 15:0", "G", "652", 10600, "SFA 15:0"),
    USDANutrient(1300, "SFA 17:0", "G", "653", 10800, "SFA 17:0"),
    USDANutrient(1301, "SFA 24:0", "G", "654", 11300, "SFA 24:0"),
    USDANutrient(1302, "Wax Esters(Total Wax)", "G", "661", 999999, "Wax Esters(Total Wax)"),
    USDANutrient(1303, "TFA 16:1 t", "G", "662", 15520, "TFA 16:1 t"),
    USDANutrient(1304, "TFA 18:1 t", "G", "663", 15521, "TFA 18:1 t"),
    USDANutrient(1305, "TFA 22:1 t", "G", "664", 15550, "TFA 22:1 t"),
    USDANutrient(1306, "TFA 18:2 t not further defined", "G", "665", 15610, "TFA 18:2 t not further defined"),
    USDANutrient(1307, "PUFA 18:2 i", "G", "666", 13350, "PUFA 18:2 i"),
    USDANutrient(1308, "PUFA 18:2 t,c", "G", "667", 13500, "PUFA 18:2 t,c"),
    USDANutrient(1309, "PUFA 18:2 c,t", "G", "668", 13400, "PUFA 18:2 c,t"),
    USDANutrient(1310, "TFA 18:2 t,t", "G", "669", 15615, "TFA 18:2 t,t"),
    USDANutrient(1311, "PUFA 18:2 CLAs", "G", "670", 13300, "PUFA 18:2 CLAs"),
    USDANutrient(1312, "MUFA 24:1 c", "G", "671", 12800, "MUFA 24:1 c"),
    USDANutrient(1313, "PUFA 20:2 n-6 c,c", "G", "672", 14300, "PUFA 20:2 n-6 c,c"),
    USDANutrient(1314, "MUFA 16:1 c", "G", "673", 11800, "MUFA 16:1 c"),
    USDANutrient(1315, "MUFA 18:1 c", "G", "674", 12200, "MUFA 18:1 c"),
    USDANutrient(1316, "PUFA 18:2 n-6 c,c", "G", "675", 13200, "PUFA 18:2 n-6 c,c"),
    USDANutrient(1317, "MUFA 22:1 c", "G", "676", 12600, "MUFA 22:1 C"),
    USDANutrient(1318, "Fatty acids, saturated, other", "G", "677", 999999, "Fatty Acids, saturated, other"),
    USDANutrient(1319, "Fatty acids, monounsat., other", "G", "678", 999999, "Fatty Acids, monounsat., other"),
    USDANutrient(1320, "Fatty acids, polyunsat., other", "G", "679", 999999, "Fatty Acids, polyunsat., other"),
    USDANutrient(1321, "PUFA 18:3 n-6 c,c,c", "G", "685", 14100, "PUFA 18:3 n-6 c,c,c"),
    USDANutrient(1322, "SFA 19:0", "G", "686", 11000, "SFA 19:0"),
    USDANutrient(1323, "MUFA 17:1", "G", "687", 12000, "MUFA 17:1"),
    USDANutrient(1324, "PUFA 16:2", "G", "688", 13000, "PUFA 16:2"),
    USDANutrient(1325, "PUFA 20:3", "G", "689", 14400, "PUFA 20:3"),
    USDANutrient(1326, "Fatty acids, total sat., NLEA", "G", "690", 999999, "Fatty Acids, total sat., NLEA"),
    USDANutrient(
        1327, "Fatty acids, total monounsat., NLEA", "G", "691", 999999, "Fatty Acids, total monounsat., NLEA"
    ),
    USDANutrient(
        1328, "Fatty acids, total polyunsat., NLEA", "G", "692", 999999, "Fatty Acids, total polyunsat., NLEA"
    ),
    USDANutrient(1329, "Fatty acids, total trans-monoenoic", "G", "693", 15500, "Fatty Acids, total trans-monoenoic"),
    USDANutrient(1330, "Fatty acids, total trans-dienoic", "G", "694", 15601, "Fatty Acids, total trans-dienoic"),
    USDANutrient(1331, "Fatty acids, total trans-polyenoic", "G", "695", 15619, "Fatty Acids, total trans-polyenoic"),
    USDANutrient(1332, "SFA 13:0", "G", "696", 10400, "SFA 13:0"),
    USDANutrient(1333, "MUFA 15:1", "G", "697", 11600, "MUFA 15:1"),
    USDANutrient(1334, "PUFA 22:2", "G", "698", 15100, "PUFA 22:2"),
    USDANutrient(1335, "SFA 11:0", "G", "699", 10200, "SFA 11:0"),
    USDANutrient(1336, "ORAC, Hydrophyllic", "UMOL_TE", "706", None, "ORAC, Hydrophyllic (umol_te)"),
    USDANutrient(1337, "ORAC, Lipophillic", "UMOL_TE", "707", None, "ORAC, Lipophillic (umol_te)"),
    USDANutrient(1338, "ORAC, Total", "UMOL_TE", "708", None, "ORAC, Total (umol_te)"),
    USDANutrient(1339, "Total Phenolics", "MG_GAE", "709", None, "Total Phenolics (mg_gae)"),
    USDANutrient(1340, "Daidzein", "MG", "710", 19100, "Daidzein"),
    USDANutrient(1341, "Genistein", "MG", "711", 19200, "Genistein"),
    USDANutrient(1342, "Glycitein", "MG", "712", 19300, "Glycitein"),
    USDANutrient(1343, "Isoflavones", "MG", "713", 19000, "Isoflavones"),
    USDANutrient(1344, "Biochanin A", "MG", "714", 999999, "Biochanin A"),
    USDANutrient(1345, "Formononetin", "MG", "715", 999999, "Formononetin"),
    USDANutrient(1346, "Coumestrol", "MG", "716", 999999, "Coumestrol"),
    USDANutrient(1347, "Flavonoids, total", "MG", "729", 999999, "Total Flavonoids"),
    USDANutrient(1348, "Anthocyanidins", "MG", "730", 19400, "Anthocyanidins"),
    USDANutrient(1349, "Cyanidin", "MG", "731", 19500, "Cyanidin"),
    USDANutrient(1350, "Proanthocyanidin (dimer-A linkage)", "MG", "732", 19510, "Proanthocyanidin (dimer-A Linkage)"),
    USDANutrient(1351, "Proanthocyanidin monomers", "MG", "733", 19520, "Proanthocyanidin Monomers"),
    USDANutrient(1352, "Proanthocyanidin dimers", "MG", "734", 19530, "Proanthocyanidin Dimers"),
    USDANutrient(1353, "Proanthocyanidin trimers", "MG", "735", 19540, "Proanthocyanidin Trimers"),
    USDANutrient(1354, "Proanthocyanidin 4-6mers", "MG", "736", 19550, "Proanthocyanidin 4-6mers"),
    USDANutrient(1355, "Proanthocyanidin 7-10mers", "MG", "737", 19560, "Proanthocyanidin 7-10mers"),
    USDANutrient(
        1356, "Proanthocyanidin polymers (>10mers)", "MG", "738", 19570, "Proanthocyanidin Polymers (>10mers)"
    ),
    USDANutrient(1357, "Delphinidin", "MG", "741", 19600, "Delphinidin"),
    USDANutrient(1358, "Malvidin", "MG", "742", 19700, "Malvidin"),
    USDANutrient(1359, "Pelargonidin", "MG", "743", 19800, "Pelargonidin"),
    USDANutrient(1360, "Peonidin", "MG", "745", 19900, "Peonidin"),
    USDANutrient(1361, "Petunidin", "MG", "746", 20000, "Petunidin"),
    USDANutrient(1362, "Flavans, total", "MG", "747", 20100, "Total Flavans"),
    USDANutrient(1363, "Catechins, total", "MG", "748", 20200, "Total Catechins"),
    USDANutrient(1364, "Catechin", "MG", "749", 20300, "Catechin"),
    USDANutrient(1365, "Epigallocatechin", "MG", "750", 20400, "Epigallocatechin"),
    USDANutrient(1366, "Epicatechin", "MG", "751", 20500, "Epicatechin"),
    USDANutrient(1367, "Epicatechin-3-gallate", "MG", "752", 20600, "Epicatechin-3-Gallate"),
    USDANutrient(1368, "Epigallocatechin-3-gallate", "MG", "753", 20700, "Epigallocatechin-3-Gallate"),
    USDANutrient(1369, "Procyanidins, total", "MG", "754", 20800, "Total Procyanidins"),
    USDANutrient(1370, "Theaflavins", "MG", "755", 20900, "Theaflavins"),
    USDANutrient(1371, "Thearubigins", "MG", "756", 21000, "Thearubigins"),
    USDANutrient(1372, "Flavanones, total", "MG", "757", 21200, "Flavanones"),
    USDANutrient(1373, "Eriodictyol", "MG", "758", 21300, "Eriodictyol"),
    USDANutrient(1374, "Hesperetin", "MG", "759", 21400, "Hesperetin"),
    USDANutrient(1375, "Isosakuranetin", "MG", "760", 21500, "Isosakuranetin"),
    USDANutrient(1376, "Liquiritigenin", "MG", "761", 21600, "Liquiritigenin"),
    USDANutrient(1377, "Naringenin", "MG", "762", 21700, "Naringenin"),
    USDANutrient(1378, "Flavones, total", "MG", "768", 21800, "Flavones"),
    USDANutrient(1379, "Apigenin", "MG", "770", 21900, "Apigenin"),
    USDANutrient(1380, "Chrysoeriol", "MG", "771", 22000, "Chrysoeriol"),
    USDANutrient(1381, "Diosmetin", "MG", "772", 22100, "Diosmetin"),
    USDANutrient(1382, "Luteolin", "MG", "773", 22200, "Luteolin"),
    USDANutrient(1383, "Nobiletin", "MG", "781", 22300, "Nobiletin"),
    USDANutrient(1384, "Sinensetin", "MG", "782", 22400, "Sinensetin"),
    USDANutrient(1385, "Tangeretin", "MG", "783", 22500, "Tangeretin"),
    USDANutrient(1386, "Flavonols, total", "MG", "784", 22600, "Flavonols"),
    USDANutrient(1387, "Isorhamnetin", "MG", "785", 22700, "Isorhamnetin"),
    USDANutrient(1388, "Kaempferol", "MG", "786", 22800, "Kaempferol"),
    USDANutrient(1389, "Limocitrin", "MG", "787", 22900, "Limocitrin"),
    USDANutrient(1390, "Myricetin", "MG", "788", 23000, "Myricetin"),
    USDANutrient(1391, "Quercetin", "MG", "789", 23100, "Quercetin"),
    USDANutrient(1392, "Theogallin", "MG", "790", 21100, "Theogallin"),
    USDANutrient(1393, "Theaflavin -3,3' -digallate", "MG", "791", None, "Theaflavin -3"),
    USDANutrient(1394, "Theaflavin -3' -gallate", "MG", "792", None, "Theaflavin -3' -Gallate"),
    USDANutrient(1395, "Theaflavin -3 -gallate", "MG", "793", None, "Theaflavin -3 -Gallate"),
    USDANutrient(1396, "(+) -Gallo catechin", "MG", "794", None, "(+) -Gallo Catechin"),
    USDANutrient(1397, "(+)-Catechin 3-gallate", "MG", "795", None, "(+)-Catechin 3-Gallate"),
    USDANutrient(1398, "(+)-Gallocatechin 3-gallate", "MG", "796", None, "(+)-Gallocatechin 3-Gallate"),
    USDANutrient(1399, "Mannose", "G", "801", 999999, "Mannose"),
    USDANutrient(1400, "Triose", "G", "803", 999999, "Triose"),
    USDANutrient(1401, "Tetrose", "G", "804", 999999, "Tetrose"),
    USDANutrient(1402, "Other Saccharides", "G", "805", 999999, "Other Saccharides"),
    USDANutrient(1403, "Inulin", "G", "806", 999999, "Inulin"),
    USDANutrient(1404, "PUFA 18:3 n-3 c,c,c (ALA)", "G", "851", 14000, "Omega-3 (ALA)"),
    USDANutrient(1405, "PUFA 20:3 n-3", "G", "852", 14500, "PUFA 20:3 n-3"),
    USDANutrient(1406, "PUFA 20:3 n-6", "G", "853", 14600, "PUFA 20:3 n-6"),
    USDANutrient(1407, "PUFA 2:4 n-3", "G", "854", 14800, "PUFA 2:4 n-3"),
    USDANutrient(1408, "PUFA 2:4 n-6", "G", "855", 14900, "PUFA 2:4 n-6"),
    USDANutrient(1409, "PUFA 18:3i", "G", "856", 14200, "PUFA 18:3i"),
    USDANutrient(1410, "PUFA 21:5", "G", "857", 15100, "PUFA 21:5"),
    USDANutrient(1411, "PUFA 22:4", "G", "858", 15160, "PUFA 22:4"),
    USDANutrient(1412, "MUFA 18:1-11 t (18:1t n-7)", "G", "859", 12310, "MUFA 18:1-11 t (18:1t n-7)"),
    USDANutrient(1413, "MUFA 18:1-11 c (18:1c n-7)", "G", "860", 12210, "MUFA 18:1-11 c (18:1c n-7)"),
    USDANutrient(1414, "PUFA 20:3 n-9", "G", "861", 14650, "PUFA 20:3 n-9"),
    USDANutrient(2000, "Sugars, total including NLEA", "G", "269", 1510, "Sugars, total including NLEA"),
    USDANutrient(2003, "SFA 5:0", "G", "632", 9850, "SFA 5:0"),
    USDANutrient(2004, "SFA 7:0", "G", "633", 9950, "SFA 7:0"),
    USDANutrient(2005, "SFA 9:0", "G", "634", 10050, "SFA 9:0"),
    USDANutrient(2006, "SFA 21:0", "G", "681", 11150, "SFA 21:0"),
    USDANutrient(2007, "SFA 23:0", "G", "682", 11250, "SFA 23:0"),
    USDANutrient(2008, "MUFA 12:1", "G", "635", 11450, "MUFA 12:1"),
    USDANutrient(2009, "MUFA 14:1 c", "G", "822", 11501, "MUFA 14:1 c"),
    USDANutrient(2010, "MUFA 17:1 c", "G", "825", 12001, "MUFA 17:1 c"),
    USDANutrient(2011, "TFA 17:1 t", "G", "826", 15525, "TFA 17:1 t"),
    USDANutrient(2012, "MUFA 20:1 c", "G", "829", 12401, "MUFA 20:1 c"),
    USDANutrient(2013, "TFA 20:1 t", "G", "830", 15540, "TFA 20:1 t"),
    USDANutrient(2014, "MUFA 22:1 n-9", "G", "676.1", 12601, "MUFA 22:1 n-9"),
    USDANutrient(2015, "MUFA 22:1 n-11", "G", "676.2", 12602, "MUFA 22:1 n-11"),
    USDANutrient(2016, "PUFA 18:2 c", "G", "831", 13150, "PUFA 18:2 c"),
    USDANutrient(2017, "TFA 18:2 t", "G", "832", 15611, "TFA 18:2 t"),
    USDANutrient(2018, "PUFA 18:3 c", "G", "833", 13910, "PUFA 18:3 c"),
    USDANutrient(2019, "TFA 18:3 t", "G", "834", 15660, "TFA 18:3 t"),
    USDANutrient(2020, "PUFA 20:3 c", "G", "835", 14450, "PUFA 20:3 c"),
    USDANutrient(2021, "PUFA 22:3", "G", "683", 14675, "PUFA 22:3"),
    USDANutrient(2022, "PUFA 2:4 c", "G", "836", 14750, "PUFA 2:4 c"),
    USDANutrient(2023, "PUFA 2:5 c", "G", "837", 14950, "PUFA 2:5 c"),
    USDANutrient(2024, "PUFA 22:5 c", "G", "838", 15150, "PUFA 22:5 c"),
    USDANutrient(2025, "PUFA 22:6 c", "G", "839", 15250, "PUFA 22:6 c"),
    USDANutrient(2026, "PUFA 20:2 c", "G", "840", 14250, "PUFA 20:2 c"),
    USDANutrient(2027, "Proximate", "G", "200", 999999, "Proximate"),
    USDANutrient(2028, "trans-beta-Carotene", "UG", "321.2", 7444, "Trans-Beta-Carotene"),
    USDANutrient(2029, "trans-Lycopene", "UG", "337.2", 7534, "Trans-Lycopene"),
    USDANutrient(2032, "Cryptoxanthin, alpha", "UG", "335", 7461, "Cryptoxanthin, alpha"),
    USDANutrient(2033, "Total dietary fiber (AOAC 2011.25)", "G", "293", 1300, "Total Dietary Fiber (AOAC 2011.25)"),
    USDANutrient(2034, "Insoluble dietary fiber (IDF)", "G", "293.1", 1310, "Insoluble Dietary Fiber (IDF)"),
    USDANutrient(2035, "Soluble dietary fiber (SDFP+SDFS)", "G", "293.2", 1320, "Soluble Dietary Fiber (SDPF+SDFS)"),
    USDANutrient(2036, "Soluble dietary fiber (SDFP)", "G", "954", 1324, "Soluble Dietary Fiber (SDFP)"),
    USDANutrient(2037, "Soluble dietary fiber (SDFS)", "G", "953", 1326, "Soluble Dietary Fiber (SDFS)"),
    USDANutrient(
        2038,
        "High Molecular Weight Dietary Fiber (HMWDF) (IDF+ SDFP)",
        "G",
        "293.3",
        1340,
        "High Molecular Weight Dietary Fiber (HMWDF) (IDF+ SDFP)",
    ),
    USDANutrient(2039, "Carbohydrates", "G", "956", 1100, "Carbohydrates"),
    USDANutrient(2040, "Other carotenoids", "UG", "955", 7510, "Other Carotenoids"),
    USDANutrient(2041, "Tocopherols and tocotrienols", "MG", "323.99", 7900, "Tocopherols and Tocotrienols"),
    USDANutrient(2042, "Amino acids", "G", "500", 16250, "Amino Acids"),
    USDANutrient(2043, "Minerals", "MG", "300", 5200, "Minerals"),
    USDANutrient(2044, "Lipids", "G", "950", 9600, "Lipids"),
    USDANutrient(2045, "Proximates", "G", "951", 50, "Proximates"),
    USDANutrient(2046, "Vitamins and Other Components", "G", "952", 6250, "Vitamins and Other Components"),
    USDANutrient(2047, "Energy (Atwater General Factors)", "KCAL", "957", 280, "Energy (Atwater General Factors)"),
    USDANutrient(2048, "Energy (Atwater Specific Factors)", "KCAL", "958", 290, "Energy (Atwater Specific Factors)"),
    USDANutrient(2049, "Daidzin", "MG", "717", 19310, "Daidzin"),
    USDANutrient(2050, "Genistin", "MG", "718", 19320, "Genistin"),
    USDANutrient(2051, "Glycitin", "MG", "719", 19330, "Glycitin"),
    USDANutrient(2052, "Delta-7-Stigmastenol", "MG", "", 16226, "Delta-7-Stigmastenol"),
    USDANutrient(2053, "Stigmastadiene", "MG", "", 15801, "Stigmastadiene"),
    USDANutrient(2054, "Total Tocotrienols", "MG", "", 7902, "Total Tocotrienols"),
    USDANutrient(2055, "Total Tocopherols", "MG", "", 7901, "Total Tocopherols"),
    USDANutrient(2057, "Ergothionine", "MG", "", 16255, "Ergothionine"),
    USDANutrient(2058, "Beta-glucan", "G", "", 1327, "Beta-glucan"),
    USDANutrient(2059, "Vitamin D4", "UG", "", 8730, "Vitamin D4"),
    USDANutrient(2060, "Ergosta-7-enol", "MG", "", 16210, "Ergosta-7-enol"),
    USDANutrient(2061, "Ergosta-7,22-dienol", "MG", "", 16211, "Ergosta-7,22-dienol"),
    USDANutrient(2062, "Ergosta-5,7-dienol", "MG", "", 16211, "Ergosta-5,7-dienol"),
    USDANutrient(2063, "Verbascose", "G", "", 2450, "Verbascose"),
    USDANutrient(2064, "Oligiosaccharides", "MG", "", 2250, "Oligiosaccharides"),
]

EQUIVALENT_NUTRIENTS: list[frozenset] = [frozenset([1008, 2047, 2048])]
ALTERNATE_UNIT_NAME: dict[str, str] = {"UG": "MCG"}
