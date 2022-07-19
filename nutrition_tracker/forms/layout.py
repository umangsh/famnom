"""Form layout methods, generate crispy layouts for all forms and formsets."""
from __future__ import annotations

import re
import uuid
from typing import Any, Sequence

from bs4 import BeautifulSoup
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import HTML, TEMPLATE_PACK, Div, Field, Layout, LayoutObject, Submit
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.utils import form as form_utils

SPACER_CSS: str = "mb-1 mx-auto"


class ThresholdDiv(Div):
    """Div Layout for Threshold fields."""

    def _process_rendered_fields(self, fields_string: str) -> str:  # pylint: disable=no-self-use
        """Modify rendered fields. This is super hacky, but there is no other way to modify individual rendered fields inside a div with crispy forms."""
        soup = BeautifulSoup(fields_string, "html.parser")

        parent_div = soup.findChildren("div", recursive=False)[0]
        parent_div["class"].append(SPACER_CSS)

        threshold_divs = soup.findAll("div", id=re.compile(".*threshold.*"))
        if not threshold_divs:
            return fields_string

        threshold_div = threshold_divs[0]
        children = threshold_div.findChildren("div", recursive=False)
        threshold_content = children[0]
        threshold_content["id"] = threshold_div["id"]
        threshold_content["class"] = "col-lg-1 pl-0 mb-1"

        label_div = soup.findAll("label", class_="col-form-label")[0]
        label_div.insert_after(threshold_content)

        input_div = soup.findAll("div", class_="threshold-value")[0]
        classes = input_div["class"]

        if not classes:
            return fields_string

        class_ = None
        for _class in classes:
            if "col-lg-" in _class:
                _a, _b = _class.split("col-lg-")
                _b = int(_b) - 1
                class_ = f"col-lg-{_b}"
                break

        if not class_:
            return fields_string

        input_div["class"] = f"{class_} pl-0 mb-1"
        threshold_div.decompose()
        return soup.prettify()

    def render(
        self, form: Any, form_style: Any, context: Any, template_pack: Any = TEMPLATE_PACK, **kwargs: Any
    ) -> str:
        """Render ThresholdDiv layout."""
        fields = super().get_rendered_fields(form, form_style, context, template_pack, **kwargs)
        fields = self._process_rendered_fields(fields)

        template = self.get_template_name(template_pack)
        return render_to_string(template, {"div": self, "fields": fields})


# The following classes are defined to extend crispy layouts
# to include user defined parent css class (mx-auto for now).
class CustomField(Field):
    """Custom Field layout."""

    template = "nutrition_tracker/layouts/field.html"


class CustomFormActions(FormActions):
    """Custom FormActions layout."""

    template = "nutrition_tracker/layouts/formactions.html"


class BarcodeCustomField(Field):
    """Custom BarcodeField layout."""

    template = "nutrition_tracker/layouts/barcode_field.html"


class Formset(LayoutObject):
    """Custom Formset layout."""

    template = "nutrition_tracker/layouts/formset.html"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        formset_name: str,
        formset_helper_name: str,
        add_class: str = "",
        delete_class: str = "",
        add_js: str = "",
        remove_js: str = "",
    ) -> None:
        self.formset_name = formset_name
        self.formset_helper_name = formset_helper_name
        self.add_class = add_class
        self.delete_class = delete_class
        self.add_js = add_js
        self.remove_js = remove_js

    def render(  # pylint: disable=unused-argument
        self, formset: Any, form_style: Any, context: Any, template_pack: Any = TEMPLATE_PACK
    ) -> str:
        """Render formset layout."""
        formset = context[self.formset_name]
        formset_helper = context[self.formset_helper_name]
        context.update(
            {
                "formset": formset,
                "formset_helper": formset_helper,
                "add_class": self.add_class,
                "delete_class": self.delete_class,
                "add_js": self.add_js,
                "remove_js": self.remove_js,
            }
        )
        return render_to_string(self.__class__.template, context.flatten())


def _separator() -> list[LayoutObject]:
    """Separator layout between other LayoutObjects like Div."""
    return [
        Div(css_class="clearfix"),
    ]


def _food_details() -> list[LayoutObject]:
    """Food metadata layout fields, includes brand metadata."""
    return [
        "external_id",
        BarcodeCustomField("gtin_upc", wrapper_class=SPACER_CSS, onchange="checkbarcodeexists();"),
        HTML(
            f"<small id='gtin_upc_message' class='d-none offset-lg-4 loading text-muted'>{_('Barcode found, redirecting')}</small>"
        ),
        Field("name", wrapper_class=SPACER_CSS),
        Field("brand_name", wrapper_class=SPACER_CSS),
        Field("subbrand_name", wrapper_class=SPACER_CSS),
        Field("brand_owner", wrapper_class=SPACER_CSS),
        Field("category_id", wrapper_class=SPACER_CSS),
    ]


def _recipe_details() -> list[LayoutObject]:
    """Recipe metadata layout fields."""
    return [
        "external_id",
        Field("name", wrapper_class=SPACER_CSS),
        Field("recipe_date", wrapper_class=SPACER_CSS),
    ]


def _meal_details() -> list[LayoutObject]:
    """Meal metadata layout fields."""
    return [
        "external_id",
        Field("meal_type", wrapper_class=SPACER_CSS),
        Field("meal_date", wrapper_class=SPACER_CSS),
    ]


def _quantity_and_portion(readonly: bool = False) -> list[LayoutObject]:
    """Servings layout fields."""
    onchange: str = "updateNutrients();"
    return [
        (
            Field("serving", wrapper_class=SPACER_CSS, readonly=True, onchange=onchange)
            if readonly
            else Field("serving", wrapper_class=SPACER_CSS, onchange=onchange)
        ),
        (
            Field("quantity", wrapper_class=SPACER_CSS, readonly=True, onchange=onchange)
            if readonly
            else Field("quantity", wrapper_class=SPACER_CSS, onchange=onchange)
        ),
    ]


def _servings() -> list[LayoutObject]:
    """Food portion layout fields."""
    return [
        Div(
            HTML(f"<p class='lead m-0 font-weight-bold'>{_('Servings')}</p>"),
            css_class="py-3",
        ),
        Div(
            Formset("servings", "servings_helper", add_class="offset-lg-4"),
            css_class="font-size-12",
        ),
    ]


def _members(header: str, formset_name: str, formset_helper: str, add_js: str, remove_js: str) -> list[LayoutObject]:
    """Food/Recipe members layout fields."""
    return [
        Div(
            HTML(f"<p class='lead m-0 font-weight-bold'>{header}</p>"),
            css_class="py-3",
        ),
        Div(
            Formset(formset_name, formset_helper, add_class="offset-lg-4", add_js=add_js, remove_js=remove_js),
            css_class="font-size-12",
        ),
    ]


def _food_members() -> list[LayoutObject]:
    """Food members layout fields."""
    header: str = _("Add foods from your Kitchen")
    return _members(
        header, "food_members", "food_members_helper", add_js="initFoodsDropdown();", remove_js="updateNutrients();"
    )


def _recipe_members() -> list[LayoutObject]:
    """Food members layout fields."""
    header: str = _("Add recipes from your Kitchen")
    return _members(
        header,
        "recipe_members",
        "recipe_members_helper",
        add_js="initRecipesDropdown();",
        remove_js="updateNutrients();",
    )


def _nutrition() -> list[LayoutObject]:
    """Nutrition layout fields."""
    return [
        Div(
            HTML(f"<p class='lead m-0 font-weight-bold'>{_('Nutrition details')}</p>"),
            css_class="py-3",
        ),
        Div(
            *[
                Field(form_utils.get_field_name(id_), wrapper_class=SPACER_CSS, onchange=f"updateNutrient({id_})")
                for id_ in constants.FORM_NUTRIENT_IDS
            ],
            css_class="font-size-12",
        ),
    ]


def _submit(submit_text: str, cancel_url: str, offset: bool = True, **kwargs: Any) -> list[LayoutObject]:
    """Submit button layout fields."""
    fields: list[LayoutObject] = [
        Submit("save", submit_text, onclick="unhideSubmitSpinner()", **kwargs),
        HTML('<a class="btn btn-light" href="{% url \'' + cancel_url + "' %}\">" + _("Cancel") + "</a>"),
        HTML(
            '<div id="submit_spinner" class="spinner-border spinner-border-sm text-primary ml-1 d-none"'
            'role="status"><span class="sr-only">Loading...</span></div>'
        ),
    ]
    return [CustomFormActions(*fields) if offset else Div(*fields)]


def food() -> Layout:
    """Food form layout."""
    fields = {}
    fields["metadata"] = _food_details()
    fields["servings"] = _servings()
    fields["separator"] = _separator()
    fields["nutrition"] = _nutrition()
    fields["submit"] = _submit(_("Save Food"), constants.URL_MY_FOODS)
    return Layout(
        *fields["metadata"], *fields["servings"], *fields["separator"], *fields["nutrition"], *fields["submit"]
    )


def recipe() -> Layout:
    """Recipe form layout."""
    fields = {}
    fields["metadata"] = _recipe_details()
    fields["servings"] = _servings()
    fields["separator"] = _separator()
    fields["food_members"] = _food_members()
    fields["recipe_members"] = _recipe_members()
    fields["submit"] = _submit(_("Save Recipe"), constants.URL_MY_RECIPES)
    return Layout(
        *fields["metadata"],
        *fields["food_members"],
        *fields["separator"],
        *fields["recipe_members"],
        *fields["separator"],
        *fields["servings"],
        *fields["separator"],
        *fields["submit"],
    )


def meal() -> Layout:
    """Meal form layout."""
    fields = {}
    fields["metadata"] = _meal_details()
    fields["separator"] = _separator()
    fields["food_members"] = _food_members()
    fields["recipe_members"] = _recipe_members()
    fields["submit"] = _submit(_("Save Meal"), constants.URL_MY_MEALS)
    return Layout(
        *fields["metadata"],
        *fields["food_members"],
        *fields["separator"],
        *fields["recipe_members"],
        *fields["separator"],
        *fields["submit"],
    )


def log() -> Layout:
    """Log form layout."""
    fields = {}
    fields["metadata"] = _meal_details()
    fields["portion"] = _quantity_and_portion()
    fields["flags"] = [CustomField("is_available")]
    fields["submit"] = _submit(_("Log"), constants.URL_HOME)
    return Layout(*fields["metadata"], *fields["portion"], *fields["flags"], *fields["submit"])


def food_portion(formtag_prefix: str, minimal: bool = False) -> Layout:
    """Food portion form layout."""
    return Layout(
        Div(
            Div(css_class="clearfix"),
            Field("servings_per_container", wrapper_class=SPACER_CSS, onchange="updateServingsPerContainer()")
            if not minimal
            else None,
            Field("household_quantity", wrapper_class=SPACER_CSS, onchange="updateDisplayServing()"),
            Field("measure_unit", wrapper_class=SPACER_CSS, onchange="updateDisplayServing()"),
            Field("serving_size", wrapper_class=SPACER_CSS, onchange="updateDisplayServing()"),
            Field("serving_size_unit", wrapper_class=SPACER_CSS, onchange="updateDisplayServing()"),
            Field("DELETE"),
            css_class=f"formset_row-{formtag_prefix}",
        ),
    )


def _member(formtag_prefix: str, css_class: str, readonly: bool = False) -> Layout:
    """Food/Recipe member layout."""
    fields = {}
    fields["separator"] = _separator()
    fields["portion"] = _quantity_and_portion(readonly=readonly)
    return Layout(
        Div(
            *fields["separator"],
            Field(
                "child_external_id",
                wrapper_class=SPACER_CSS,
                css_class=css_class,
                onchange="getServings(this);getNutrients(this, true);",
            ),
            *fields["portion"],
            Field("DELETE"),
            css_class=f"formset_row-{formtag_prefix}",
        ),
    )


def _food_member(formtag_prefix: str, readonly: bool = False) -> Layout:
    """Food member layout."""
    return _member(formtag_prefix, "foods-dropdown", readonly=readonly)


def _recipe_member(formtag_prefix: str, readonly: bool = False) -> Layout:
    """Recipe member layout."""
    return _member(formtag_prefix, "recipes-dropdown", readonly=readonly)


def create_food_member(formtag_prefix: str) -> Layout:
    """Create food member layout."""
    return _food_member(formtag_prefix, readonly=True)


def edit_food_member(formtag_prefix: str) -> Layout:
    """Edit food member layout."""
    return _food_member(formtag_prefix, readonly=False)


def create_recipe_member(formtag_prefix: str) -> Layout:
    """Create recipe member layout."""
    return _recipe_member(formtag_prefix, readonly=True)


def edit_recipe_member(formtag_prefix: str) -> Layout:
    """Edit recipe member layout."""
    return _recipe_member(formtag_prefix, readonly=False)


def nutrition() -> Layout:
    """Nutrition form layout."""
    fields = {}
    fields["profile"] = [
        Field("date_of_birth", wrapper_class=SPACER_CSS),
        CustomField("is_pregnant"),
    ]
    fields["fda"] = [
        Div(
            Div(
                HTML(
                    '<a class="btn btn-outline-primary btn-sm" onclick="updateFDARDIs()">'
                    + _("Use FDA Recommended Daily Intake (RDIs)")
                    + "</a>"
                ),
                css_class="offset-lg-3",
            ),
            Div(
                HTML(
                    '<small id="fda_rdi_common" class="text-muted">'
                    + _("Click to fill FDA recommended RDIs.")
                    + "</small>"
                ),
                HTML(
                    '<small id="fda_rdi_'
                    + str(constants.FDA_ADULT)
                    + '" class="d-none text-muted">'
                    + _("* RDIs for adults and children >= 4 years.")
                    + "</small>"
                ),
                HTML(
                    '<small id="fda_rdi_'
                    + str(constants.FDA_INFANT)
                    + '" class="d-none text-muted">'
                    + _("* RDIs for infants through 12 months.")
                    + "</small>"
                ),
                HTML(
                    '<small id="fda_rdi_'
                    + str(constants.FDA_CHILDREN)
                    + '" class="d-none text-muted">'
                    + _("* RDIs for children 1 through 3 years.")
                    + "</small>"
                ),
                HTML(
                    '<small id="fda_rdi_'
                    + str(constants.FDA_PREGNANT)
                    + '" class="d-none text-muted">'
                    + _("* RDIs for pregnant and/or lactating women.")
                    + "</small>"
                ),
                css_class="offset-lg-3 mb-1",
            ),
        ),
    ]
    fields["nutrients"] = [
        Div(
            *[
                ThresholdDiv(form_utils.get_field_name(id_), form_utils.get_threshold_field_name(id_))
                for id_ in constants.TRACKER_NUTRIENT_IDS
                if id_ not in constants.LOW_COVERAGE_NUTRIENT_IDS
            ],
            css_class="nutrient-item-list",
        )
    ]
    fields["submit"] = _submit(_("Save Goals"), constants.URL_HOME)
    return Layout(
        *fields["profile"],
        *fields["fda"],
        *fields["nutrients"],
        *fields["submit"],
    )


def profile(family_members: list[user_model.User]) -> Layout:
    """User profile layout."""
    fields = {}
    fields["profile_A"] = [
        Field("first_name", wrapper_class=SPACER_CSS),
        Field("last_name", wrapper_class=SPACER_CSS),
        Field("email", wrapper_class=SPACER_CSS),
    ]
    fields["password"] = [
        Div(
            HTML(
                '<a class="btn btn-outline-primary btn-sm" href="/accounts/password/change/">'
                + _("Change Password")
                + "</a>"
            ),
            css_class="offset-lg-3 mb-1",
        ),
    ]
    fields["profile_B"] = [
        Field("date_of_birth", wrapper_class=SPACER_CSS),
        CustomField("is_pregnant"),
        Field("family_email", wrapper_class=SPACER_CSS),
    ]

    member_string: str = ", ".join(luser.email for luser in family_members)
    if member_string:
        member_string = _("Other Members: ") + member_string

    fields["family_members"] = [
        Div(
            Div(css_class="col-lg-3 pl-0"),
            Div(
                HTML(f"<span>{_(member_string)}</span>"),
                css_class="col-lg-6 pl-0",
            ),
            css_class="form-group row mx-auto mb-2",
        ),
    ]
    fields["submit"] = _submit(_("Save Profile"), constants.URL_PROFILE)
    return Layout(
        *fields["profile_A"],
        *fields["password"],
        *fields["profile_B"],
        *fields["family_members"],
        *fields["submit"],
    )


def _mealplan_section(prefix: str, header: str, subheader: str) -> Layout:
    """Mealplan form section layout."""
    foods_field = f"{prefix}_foods"
    recipes_field = f"{prefix}_recipes"
    return [
        HTML(
            f'<div class="lead mt-4 font-weight-bold">{header}<div class="mealplan-spinner '
            'spinner-border text-primary ml-3" role="status"><span class="sr-only">'
            "Loading...</span></div></div>"
        ),
        HTML(f'<div class="mb-3 text-muted">{subheader}</div>'),
        Field(foods_field, wrapper_class=SPACER_CSS, id=foods_field, css_class="foods-dropdown"),
        Field(recipes_field, wrapper_class=SPACER_CSS, id=recipes_field, css_class="recipes-dropdown"),
    ]


def mealplan_one() -> Layout:
    """Mealplan one form layout."""
    fields = {}
    fields["available"] = _mealplan_section(
        "available", _("Step 1: Available items"), _("Add foods and recipes available in your Kitchen")
    )
    fields["must_have"] = _mealplan_section("must_have", _("Step 2: Must haves"), _("Must have foods and recipes"))
    fields["dont_have"] = _mealplan_section(
        "dont_have", _("Step 3: Don't haves"), _("Don't use these items for meal planning")
    )
    fields["dont_repeat"] = _mealplan_section(
        "dont_repeat", _("Step 4: Can't have everyday"), _("Ignore if logged in yesterday's meals")
    )
    fields["submit"] = _submit(_("Next"), constants.URL_HOME)
    return Layout(
        *fields["available"],
        *fields["must_have"],
        *fields["dont_have"],
        *fields["dont_repeat"],
        *fields["submit"],
    )


def mealplan_two(rows: Sequence[str | uuid.UUID]) -> Layout:
    """Mealplan two form layout."""
    fields = {}
    subtext: str = _(
        "Adjust food portion preferences (in g/ml), used by the planner."
        f" If unspecified, a portion size between {constants.DEFAULT_DAILY_FOOD_MIN_VALUE} and {constants.DEFAULT_DAILY_FOOD_MAX_VALUE} (g/ml) is considered "
        "for all available foods and recipes by default."
    )

    fields["form"] = [
        HTML(f"<div class='lead mt-4 font-weight-bold'>{_('Step 5: Adjust portions')}</div>"),
        HTML(f"<div class='mb-3 text-muted'>{subtext}</div>"),
        *[ThresholdDiv(form_utils.get_field_name(id_), form_utils.get_threshold_field_name(id_)) for id_ in rows],
    ]
    fields["submit"] = _submit(_("Next"), constants.URL_HOME, data_toggle="modal", data_target="#progressModal")
    return Layout(
        *fields["form"],
        *fields["submit"],
    )


def mealplan_three(rows: Sequence[str | uuid.UUID]) -> Layout:
    """Mealplan three form layout."""
    fields: dict = {}
    fields["form"] = []
    for id_ in rows:
        fields["form"].extend(
            [
                Field(form_utils.get_field_name(id_), wrapper_class=SPACER_CSS, onchange="updateTracker();"),
                Field(form_utils.get_meal_field_name(id_), wrapper_class=SPACER_CSS),
            ]
        )
    fields["submit"] = _submit(_("Save"), constants.URL_HOME, offset=False)
    return Layout(
        *fields["form"],
        *fields["submit"],
    )
