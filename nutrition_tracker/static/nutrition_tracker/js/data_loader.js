/**
 * Get and populate nutrients dropdown.
 *
 * @param {HTMLElement} elem The food/recipe DOM element.
 * @param {boolean} refresh Refresh nutrition label.
 * @param {function} doneCallback onComplete callback.
 */
function getNutrients( // eslint-disable-line no-unused-vars
    elem, refresh, doneCallback) {
  // Get object ID.
  const id = $(elem).val();
  if (!id) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_nutrient_ajax
  request = $.ajax({
    url: '/my_nutrient_ajax/' + id + '/',
    type: 'get',
    dataType: 'json',
    success: function(response) {
      $.each(response, function(i, item) {
        $(elem).parent().attr(
            'data-' + String(item['nutrient_id']), item['amount']);
      });
      if (refresh) {
        updateNutrients();
      }
    },
    complete: doneCallback,
  });
}

/**
 * Get and populate servings dropdown.
 *
 * @param {HTMLElement} elem The food/recipe DOM element.
 * @param {function} doneCallback onComplete callback.
 */
function getServings(elem, doneCallback) { // eslint-disable-line no-unused-vars
  // Get object ID.
  const id = $(elem).val();
  if (!id) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_serving_ajax
  request = $.ajax({
    url: '/my_serving_ajax/' + id + '/',
    type: 'get',
    dataType: 'json',
    success: function(response) {
      const prefix = $(elem).attr('id').slice(0, -'child_external_id'.length);
      const idQuantity = prefix + 'quantity';
      const idServing = prefix + 'serving';

      $('#' + idQuantity).attr('readonly', false);
      $('#' + idServing).attr('readonly', false);

      $('#' + idServing).empty();
      $.each(response, function(i, item) {
        $('#' + idServing).append($('<option>', {
          'value': item[0], // id
          'text': item[1]['label'], // label
          'data-gm-wt': item[1]['data-gm-wt'],
          'data-wt-unit': item[1]['data-wt-unit'],
        }));
      });
    },
    complete: doneCallback,
  });
}

/**
 * Check and redirect if barcode already exists.
 *
 * @param {function} doneCallback onComplete callback.
 */
function checkbarcodeexists( // eslint-disable-line no-unused-vars
    doneCallback) {
  const barcode = $('#id_gtin_upc').val();
  if (!barcode) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_barcode_ajax
  request = $.ajax({
    url: '/my_barcode_ajax/' + barcode + '/',
    type: 'get',
    dataType: 'json',
    success: function(response) {
      if (!response['url']) {
        return;
      }

      $('#gtin_upc_message').removeClass('d-none');
      window.setTimeout(function() {
        window.location.replace(response['url']);
      }, 2500);
    },
    complete: doneCallback,
  });
}

/**
 * Get top foods for a nutrient_id.
 *
 * @param {number} nutrientId The nutrient ID to fetch top foods.
 * @param {function} doneCallback onComplete callback.
 */
function getTopFoodsHTML( // eslint-disable-line no-unused-vars
    nutrientId, doneCallback) {
  if (!nutrientId) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to top_foods_ajax
  $.ajax({
    url: '/top_foods_ajax/' + nutrientId + '/',
    type: 'get',
    success: function(response) {
      $('.top-foods-parent').html(response);
      $('.top-foods-spinner').hide();
    },
    complete: doneCallback,
  });
}

/**
 * Get recent foods for a nutrient_id.
 *
 * @param {number} nutrientId The nutrient ID to fetch recent foods.
 * @param {function} doneCallback onComplete callback.
 */
function getRecentFoodsHTML( // eslint-disable-line no-unused-vars
    nutrientId, doneCallback) {
  if (!nutrientId) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_recent_foods_ajax
  $.ajax({
    url: '/my_recent_foods_ajax/' + nutrientId + '/',
    type: 'get',
    success: function(response) {
      $('.recent-foods-parent').html(response);
      $('.recent-foods-spinner').hide();
    },
    complete: doneCallback,
  });
}

/**
 * Get available foods for a nutrient_id.
 *
 * @param {number} nutrientId The nutrient ID to fetch available foods.
 * @param {function} doneCallback onComplete callback.
 */
function getAvailableFoodsHTML( // eslint-disable-line no-unused-vars
    nutrientId, doneCallback) {
  if (!nutrientId) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_available_foods_ajax
  $.ajax({
    url: '/my_available_foods_ajax/' + nutrientId + '/',
    type: 'get',
    success: function(response) {
      $('.available-foods-parent').html(response);
      $('.available-foods-spinner').hide();
    },
    complete: doneCallback,
  });
}

/**
 * Get tracker for a nutrient_id.
 *
 * @param {number} nutrientId The nutrient ID to fetch tracker information.
 * @param {function} doneCallback onComplete callback.
 */
function getTrackerHTML( // eslint-disable-line no-unused-vars
    nutrientId, doneCallback) {
  if (!nutrientId) {
    return;
  }

  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_tracker_ajax
  $.ajax({
    url: '/my_tracker_ajax/' + nutrientId + '/',
    type: 'get',
    success: function(response) {
      $('.tracker-parent').html(response);
      $('.tracker-spinner').hide();
    },
    complete: doneCallback,
  });
}

/**
 * Get Suggested Foods for a user.
 *
 * @param {function} doneCallback onComplete callback.
 */
function getSuggestedFoodsHTML( // eslint-disable-line no-unused-vars
    doneCallback) {
  doneCallback = doneCallback || function() {}; // ensure we have a callback

  // Fire off the request to my_tracker_ajax
  $.ajax({
    url: '/my_suggested_foods_ajax/',
    type: 'get',
    success: function(response) {
      $('.suggested-foods-parent').html(response);
      $('.suggested-foods-spinner').hide();
    },
    complete: doneCallback,
  });
}

exports.getNutrients = getNutrients;
exports.getServings = getServings;
exports.checkbarcodeexists = checkbarcodeexists;
exports.getTopFoodsHTML = getTopFoodsHTML;
exports.getRecentFoodsHTML = getRecentFoodsHTML;
exports.getAvailableFoodsHTML = getAvailableFoodsHTML;
exports.getTrackerHTML = getTrackerHTML;
exports.getSuggestedFoodsHTML = getSuggestedFoodsHTML;
