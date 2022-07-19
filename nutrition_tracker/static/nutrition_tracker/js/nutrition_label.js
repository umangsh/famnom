/**
 * Update servings per container in the nutrition label.
 */
function updateServingsPerContainer() { // eslint-disable-line no-unused-vars
  const servingsPerContainer = $(
      'input[id$="-0-servings_per_container"]').val();
  if (servingsPerContainer === undefined || servingsPerContainer.length === 0) {
    $('.nutrition-label .servings-per-container-quantity').text('');
    return;
  }
  // Flash the row
  $('.nutrition-label .servings-per-container').fadeOut(50);
  $('.nutrition-label .servings-per-container').fadeIn(100);
  $('.nutrition-label .servings-per-container-quantity').text(
      servingsPerContainer);
}

/**
 * Update serving display in the nutrition label.
 */
function updateDisplayServing() { // eslint-disable-line no-unused-vars
  const portion = parseFloat(
      $('#id_serving').find(':selected').attr('data-gm-wt'));
  if (portion) {
    // Don't update the serving if portion field exists in the form.
    return;
  }

  const servingSize = $('input[id$="-0-serving_size"]').val() || '';
  const servingSizeUnit = $('select[id$="-0-serving_size_unit"]').val() || '';
  const householdQuantity = $(
      'select[id$="-0-household_quantity"]').val() || '';
  const householdUnit = $('select[id$="-0-measure_unit"]').val() || '';

  let firstHalf = '';
  if (householdQuantity && householdUnit) {
    const householdUnitText = $(
        'select[id$="-0-measure_unit"] option:selected').text();
    firstHalf = householdQuantity + ' ' + householdUnitText;
  }

  let secondHalf = '';
  if (servingSize && servingSizeUnit) {
    secondHalf = servingSize + servingSizeUnit;
  }

  let displayServingSize = '';
  if (firstHalf && secondHalf) {
    displayServingSize = firstHalf + ' (' + secondHalf + ')';
  } else if (firstHalf) {
    displayServingSize = firstHalf;
  } else if (secondHalf) {
    displayServingSize = secondHalf;
  }

  if (displayServingSize) {
    // Flash the row
    $('.nutrition-label .serving-size-display').fadeOut(50);
    $('.nutrition-label .serving-size-display').fadeIn(100);
  }
  $('.nutrition-label .serving-size').text(displayServingSize);
}

/**
 * Updates nutrients as quantity and/or portion change.
 */
function updateNutrients() { // eslint-disable-line no-unused-vars
  // Flash the nutrient label
  $('.nutrition-label').fadeOut(50);

  const $quantity = $('#id_quantity');
  const $portion = $('#id_serving');

  if ($quantity.length && $portion.length) {
    // Food or Recipe
    const quantity = $quantity.val() || 1;

    // Update serving size
    $('.nutrition-label .serving-size').text(
        $portion.find(':selected').text());

    // Update element visibility
    if (quantity != 1) {
      $('.nutrition-label .total-amount-text').removeClass('d-none');
      $('.nutrition-label .amount-per-serving-text').addClass('d-none');
    } else {
      $('.nutrition-label .total-amount-text').addClass('d-none');
      $('.nutrition-label .amount-per-serving-text').removeClass('d-none');
    }
  }

  // Update nutrition rows
  const foodPortionSize = 100;
  const $labelNutrients = $('.nutrition-label .nutrient');
  const $members = $('select[id$="-child_external_id"]');
  $labelNutrients.each(/* @this HTMLElement */ function() {
    const id = $(this).attr('data-nutrient');
    let nutrientValue;
    if ($members.length) {
      // Recipe or Meal
      $members.each(/* @this HTMLElement */ function() {
        const base = $(this).parent().attr('data-' + id);
        if (base === undefined) {
          return;
        }

        if (isNaN(base)) {
          return;
        }

        // Ignore hidden formset rows
        const $parent= $(this).parent().parent().parent();
        if ($parent.is(':hidden')) {
          return;
        }

        if (nutrientValue === undefined) {
          nutrientValue = 0;
        }

        // Update nutrient value
        const portion = parseFloat($parent.find($(
            'select[id$="-serving"]')).find(':selected').attr('data-gm-wt'));
        const quantity = $parent.find($('input[id$="-quantity"]')).val() || 1;
        nutrientValue += (base * quantity * portion) / foodPortionSize;
      });
    } else {
      const base = $('.nutrition-label').data(id);
      if (base === undefined) {
        return;
      }
      if (isNaN(base)) {
        return;
      }
      const quantity = $quantity.val() || 1;
      const portion = parseFloat(
          $portion.find(':selected').attr('data-gm-wt'));
      nutrientValue = (base * quantity * portion) / foodPortionSize;
    }

    // Update nutrient values
    if (nutrientValue === undefined) {
      return;
    }

    $(this).find('.nutrient-quantity').text(
        parseFloat(nutrientValue.toFixed(2)));
    $(this).find('.nutrient-unit').removeClass('d-none');

    if ($(this).find('.nutrient-dv')) {
      const dvTotal = $('.nutrition-label').data('dv-' + id);
      if (dvTotal === undefined) {
        return;
      }
      const dvPercnt = (nutrientValue * 100) / dvTotal;

      // Update DV values
      $(this).find('.nutrient-dv').text(parseFloat(dvPercnt.toFixed()));
      $(this).find('.nutrient-dv-percent').removeClass('d-none');
    }
  });

  // Flash the nutrient label
  $('.nutrition-label').fadeIn(100);

  // Update the servings field as well, only applicable for recipes.
  const $parentServingSize = $('#id_servings-0-serving_size');
  const $parentServingUnit = $('#id_servings-0-serving_size_unit');

  // Update the serving unit based on the first item unit.
  if (!$parentServingUnit.find(':selected').val()) {
    const $firstFoodMemberServingUnit = $(
        '#id_food-0-serving').find(':selected').attr('data-wt-unit');
    const $firstRecipeMemberServingUnit = $(
        '#id_recipe-0-serving').find(':selected').attr('data-wt-unit');
    $parentServingUnit.val(
        $firstFoodMemberServingUnit || $firstRecipeMemberServingUnit);
  }

  let servingSize = 0;
  $members.each(/* @this HTMLElement */ function() {
    // Ignore hidden formset rows
    const $parent = $(this).parent().parent().parent();
    if ($parent.is(':hidden')) {
      return;
    }
    // Update nutrient value
    const portion = parseFloat($parent.find($(
        'select[id$="-serving"]')).find(':selected').attr('data-gm-wt')) || 0;
    const quantity = $parent.find($('input[id$="-quantity"]')).val() || 1;
    servingSize += (portion * quantity);
  });

  if (servingSize && $parentServingSize.val() < servingSize) {
    $parentServingSize.val(servingSize);
  }
}

/**
 * Updates nutrient value as form input changes.
 *
 * @param {number} id must be a number
 */
function updateNutrient(id) { // eslint-disable-line no-unused-vars
  const nutrientValue = $('#id_' + id).val();
  if ((nutrientValue === undefined) || (nutrientValue.length === 0)) {
    $('.nutrient-' + id + ' .nutrient-quantity').text('');
    $('.nutrient-' + id + ' .nutrient-unit').addClass('d-none');
    $('.nutrient-' + id + ' .nutrient-dv').text('');
    $('.nutrient-' + id + ' .nutrient-dv-percent').addClass('d-none');
    return;
  }

  // Flash the nutrient row
  $('.nutrient-' + id).fadeOut(50);

  // Flash the nutrient label
  $('.nutrient-' + id).fadeIn(100);

  // Update nutrient values
  $('.nutrient-' + id + ' .nutrient-quantity').text(nutrientValue);
  $('.nutrient-' + id + ' .nutrient-unit').removeClass('d-none');

  const dvTotal = $('.nutrition-label').data('dv-' + id);
  if (dvTotal === undefined) {
    return;
  }
  const dvPercnt = (nutrientValue * 100) / dvTotal;

  // Update DV values
  $('.nutrient-' + id + ' .nutrient-dv').text(parseFloat(dvPercnt.toFixed()));
  $('.nutrient-' + id + ' .nutrient-dv-percent').removeClass('d-none');
}

exports.updateServingsPerContainer = updateServingsPerContainer;
exports.updateDisplayServing = updateDisplayServing;
exports.updateNutrients = updateNutrients;
exports.updateNutrient = updateNutrient;
