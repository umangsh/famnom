/**
 * Updates tracker as quantities change.
 */
function updateTracker() { // eslint-disable-line no-unused-vars
  // Update nutrition rows
  const foodPortionSize = 100;
  const $trackerNutrients = $('.nutrition-tracker .nutrient');
  const $members = $('input[id^="id_"]');
  $trackerNutrients.each(/* @this HTMLElement */ function() {
    const id = $(this).attr('data-nutrient');
    let nutrientValue = parseFloat(
        $('.nutrition-tracker').attr('data-' + id) || 0);

    if ($members.length) {
      $members.each(/* @this HTMLElement */ function() {
        const base = $(this).parent().parent().attr('data-' + id);
        if (base === undefined) {
          return;
        }

        const quantity = $(this).val() || 0;
        nutrientValue += (base * quantity) / foodPortionSize;
      });
    }

    // Update nutrient values
    $(this).find('.nutrient-quantity').text(
        parseFloat(nutrientValue.toFixed(2)));

    if ($(this).find('.nutrient-dv')) {
      const dvTotal = $('.nutrition-tracker').data('dv-' + id);
      if (dvTotal === undefined) {
        return;
      }
      const dvPercnt = (nutrientValue * 100) / dvTotal;

      // Update DV values
      $(this).find('.nutrient-dv').text(parseFloat(dvPercnt.toFixed()));

      // Update progress bar
      $(this).find('.nutrient-progress').attr(
          'aria-valuenow', dvPercnt.toFixed());
      $(this).find('.nutrient-progress').attr(
          'style', 'width: ' + dvPercnt.toFixed() + '%');
    }
  });

  // Flash the nutrient label
  $('.nutrition-tracker').fadeIn(100);
}
