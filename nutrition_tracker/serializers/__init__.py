"""Serializers package."""
from drf_braces.serializers import form_serializer
from drf_braces.utils import reduce_attr_dict_from_instance

from .base import DynamicFieldsModelSerializer, NonNullModelSerializer
from .db_branded_food import DBBrandedFoodSerializer
from .db_food import DBFoodSerializer
from .food_form import FoodFormSerializer
from .form_data import FormDataSerializer
from .log import LogSerializer
from .meal_form import MealFormSerializer
from .mealplan_form import MealplanFormOneSerializer, MealplanFormTwoSerializer, MealplanFormThreeSerializer
from .nutrition import NutritionSerializer
from .recipe_form import RecipeFormSerializer
from .search_result import SearchResultSerializer
from .uuid import UUIDSerializer
from .user import UserDataSerializer
from .user_food_membership import UserFoodMembershipSerializer
from .user_food_portion import UserFoodPortionSerializer
from .user_ingredient_display import UserIngredientDisplaySerializer
from .user_ingredient_mutable import UserIngredientMutableSerializer
from .user_member_ingredient_display import UserMemberIngredientDisplaySerializer
from .user_member_recipe_display import UserMemberRecipeDisplaySerializer
from .user_meal_display import UserMealDisplaySerializer
from .user_meal_mutable import UserMealMutableSerializer
from .user_recipe_display import UserRecipeDisplaySerializer
from .user_recipe_mutable import UserRecipeMutableSerializer
from .user_preference import UserPreferenceSerializer, UserPreferenceThresholdSerializer


# DRF braces (0.3.4) doesn't process all fields from form when fields are added in __init__.
# Only base_fields are considered. Monkey patch the fix.


def get_fields(self, **kwargs):  # type: ignore
    """
    Return all the fields that should be serialized for the form.
    This is a hook provided by parent class.
    :return: dict of {'field_name': serializer_field_instance}
    """
    ret = super(form_serializer.FormSerializerBase, self).get_fields()

    field_mapping = reduce_attr_dict_from_instance(
        self,
        lambda i: getattr(getattr(i, "Meta", None), "field_mapping", {}),
        form_serializer.FORM_SERIALIZER_FIELD_MAPPING,
    )

    # Iterate over the form fields, creating an
    # instance of serializer field for each.
    instance = self.get_form()  # override: form = self.Meta.form
    for field_name, form_field in getattr(instance, "all_fields", instance.fields).items():
        # override: for field_name, form_field in getattr(form, 'all_base_fields', form.base_fields).items():
        # if field is specified as excluded field
        if field_name in getattr(self.Meta, "exclude", []):
            continue

        # if field is already defined via declared fields
        # skip mapping it from forms which then honors
        # the custom validation defined on the DRF declared field
        if field_name in ret:
            continue

        try:
            serializer_field_class = field_mapping[form_field.__class__]
        except KeyError as unmapped_field:
            raise TypeError(
                "{field} is not mapped to a serializer field. "
                "Please add {field} to {serializer}.Meta.field_mapping. "
                "Currently mapped fields: {mapped}".format(
                    field=form_field.__class__.__name__,
                    serializer=self.__class__.__name__,
                    mapped=", ".join(sorted(i.__name__ for i in field_mapping.keys())),
                )
            ) from unmapped_field
        else:
            ret[field_name] = self._get_field(form_field, serializer_field_class)  # pylint: disable=protected-access

    return ret


form_serializer.FormSerializer.get_fields = get_fields
