/**
 * Initializes the kitchen base js.
 */
$(document).ready(function() {
  // Initialize datepickers.
  initEditDatepicker('#id_meal_date');
  initEditDatepicker('#id_recipe_date');

  // Initialize dropdowns
  initFoodsDropdown();
  initRecipesDropdown();
});
