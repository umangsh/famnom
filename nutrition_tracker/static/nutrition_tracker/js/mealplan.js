/**
 * Initializes the mealplan js.
 */
$(document).ready(function() {
  // Initialize dropdowns
  initFoodsDropdown(placeholder='Add foods', closeOnSelect=false);
  initRecipesDropdown(placeholder='Add recipes', closeOnSelect=false);

  // Initialize preloaded dropdowns
  initPreloadedDropdown(
      '#available_foods', '/my_foods/', 'is_available', '');
  initPreloadedDropdown(
      '#available_recipes', '/my_recipes/', 'is_available', '');
  initPreloadedDropdown(
      '#must_have_foods', '/my_foods/', 'is_not_zeroable', '');
  initPreloadedDropdown(
      '#must_have_recipes', '/my_recipes/', 'is_not_zeroable', '');
  initPreloadedDropdown(
      '#dont_have_foods', '/my_foods/', 'is_not_allowed', '');
  initPreloadedDropdown(
      '#dont_have_recipes', '/my_recipes/', 'is_not_allowed', '');
  initPreloadedDropdown(
      '#dont_repeat_foods', '/my_foods/', 'is_not_repeatable', '');
  initPreloadedDropdown(
      '#dont_repeat_recipes', '/my_recipes/', 'is_not_repeatable', '');

  // Hide the spinners
  $(document).ajaxStop(function() {
    $('.mealplan-spinner').hide();
  });
});
