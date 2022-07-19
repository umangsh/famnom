/**
 * Initializes the edit datepicker.
 * @param {string} elem The date element.
 * @param {boolean} changeMonth Show change month in picker.
 * @param {boolean} changeYear Show change year in picker.
 */
function initEditDatepicker( // eslint-disable-line no-unused-vars
    elem, changeMonth=false, changeYear=false) {
  $(elem).datepicker({
    dateFormat: 'yy-mm-dd',
    changeMonth: changeMonth,
    changeYear: changeYear,
    yearRange: '-100:+0',
  });
}

/**
 * Initializes the browse datepicker.
 * @param {string} elem The date element.
 */
function initBrowseDatepicker(elem) { // eslint-disable-line no-unused-vars
  $(elem).datepicker({
    dateFormat: $.datepicker.RFC_2822,
    onSelect: function(date, el) {
      const selectedDate = new Date(date);
      const todaysDate = new Date().setHours(0, 0, 0, 0);
      const diffDate = selectedDate - todaysDate;
      const diffDays = Math.round(diffDate / 86400000);

      const uri = new Uri(window.location.href);
      let uriTd = uri.getQueryParamValue('td') || 0;
      if (!$.isNumeric(uriTd)) {
        uriTd = 0;
      }
      if (diffDays != uriTd) {
        uri.replaceQueryParam('td', diffDays);
        window.location.href = uri.toString();
      }
    },
  });
}

/**
 * Initialize the addToKitchen submit ajax.
 */
function initAddToKitchen() { // eslint-disable-line no-unused-vars
  const elem = '#addToKitchen';
  // Bind to the submit event of addToKitchen form.
  $(elem).submit(/* @this HTMLElement */ function(event) {
    // Prevent default posting of form
    event.preventDefault();

    $(this).find('.btn').prop('disabled', true);
    $(this).find('.btn').text('Adding ...');

    // Fire off the request to my_food_save_ajax
    request = $.ajax({
      url: '/my_food_save_ajax/',
      type: 'post',
      data: $(this).serialize(),
    });

    // Callback handler that will be called on success
    request.done(function(response, textStatus, jqXHR) {
      $(elem).find('.btn').text('Added to MyKitchen');
      $(elem).find('.btn').removeClass(
          'btn-outline-secondary').addClass('btn-success');
      $(elem).fadeOut(2000);
    });

    // Callback handler that will be called on failure
    request.fail(function(jqXHR, textStatus, errorThrown) {
      $(elem).find('.btn').text('Try again');
      $(elem).find('.btn').removeClass(
          'btn-outline-secondary').addClass('btn-danger');
    });
  });
}

/**
 * Initializes the user's timezone.
 */
function initTimezone() { // eslint-disable-line no-unused-vars
  const date = new Intl.DateTimeFormat();
  const currentDate = new Date();
  const expirationDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      currentDate.getDate() + 1,
      0, 0, 0);
  $.cookie(
      'user_tz',
      date.resolvedOptions().timeZone,
      {
        path: '/',
        secure: true,
        expires: expirationDate,
      });
}

/**
 * Initializes page tooltips.
 */
function initTooltips() { // eslint-disable-line no-unused-vars
  $('[data-toggle="tooltip"]').tooltip();
}

/**
 * Initialize a select2 ajax dropdown.
 *
 * @param {HTMLElement} elem The dropdown element.
 * @param {string} placeholder Dropdown default string.
 * @param {string} url The URL to fetch items data.
 * @param {boolean} closeOnSelect Close the dropdown on select.
 */
function initDropdown(elem, placeholder, url, closeOnSelect=true) {
  $(elem).select2({
    theme: 'bootstrap4',
    placeholder: placeholder,
    width: 'resolve',
    allowClear: true,
    closeOnSelect: closeOnSelect,
    ajax: {
      url: url,
      dataType: 'json',
      type: 'GET',
      delay: 250, // wait 250ms before request
      cache: true,
      data: function(params) {
        const query = {
          q: params.term,
          page: params.page || 1,
        };
        return query;
      },
      processResults: function(data, params) {
        params.page = params.page || 1;
        return data;
      },
    },
  });
}

/**
 * Initialize foods dropdown.
 *
 * @param {string} placeholder Dropdown default string.
 * @param {boolean} closeOnSelect Close the dropdown on select.
 */
function initFoodsDropdown( // eslint-disable-line no-unused-vars
    placeholder='Search foods', closeOnSelect=true) {
  initDropdown(
      '.foods-dropdown', placeholder, '/my_foods/', closeOnSelect);
}

/**
 * Initialize recipes dropdown.
 *
 * @param {string} placeholder Dropdown default string.
 * @param {boolean} closeOnSelect Close the dropdown on select.
 */
function initRecipesDropdown( // eslint-disable-line no-unused-vars
    placeholder='Search recipes', closeOnSelect=true) {
  initDropdown(
      '.recipes-dropdown', placeholder, '/my_recipes/', closeOnSelect);
}

/**
 * Initialize a select2 ajax dropdown with preloaded data.
 *
 * @param {HTMLElement} elem The dropdown element.
 * @param {string} url The URL to fetch items data.
 * @param {string} fs Flags set
 * @param {string} fn Flags unset
 */
function initPreloadedDropdown( // eslint-disable-line no-unused-vars
    elem, url, fs, fn) {
  $.ajax({
    type: 'GET',
    url: url,
    data: {
      fs: fs,
      fn: fn,
    },
  }).then(function(data) {
    $.each(data['results'], function(i, item) {
      // create the option and append to Select2
      const option = new Option(item.text, item.id, true, true);
      $(elem).append(option).trigger('change');
    });

    // manually trigger the `select2:select` event
    $(elem).trigger({
      type: 'select2:select',
      params: {
        data: data,
      },
    });
  });
}

/**
 * Delete a food.
 *
 * @param {document#onclick} event
 * @listens document#onclick
 */
function deleteFood(event) { // eslint-disable-line no-unused-vars
  event.stopPropagation();
  if (!confirm('Confirm delete?')) {
    event.preventDefault();
  }
}

/** Initialize search autocomplete.
 */
function initSearchAutocomplete() { // eslint-disable-line no-unused-vars
  $('.autocomplete').autoComplete({
    autoSelect: true,
    minLength: 3,
    noResultsText: '',
    resolverSettings: {
      url: '/search/',
      queryKey: 'q',
      requestThrottling: 200,
      fail: function() {},
    },
    formatResult: function(item) {
      return {
        id: item['external_id'],
        text: item['dname'],
      };
    },
  });

  $('.autocomplete').on('autocomplete.select', function(e, item) {
    window.location.assign(item['url']);
  });
}

/**
 * Initialize barcode scan if supported.
 */
function initBarcodeScan() { // eslint-disable-line no-unused-vars
  if (!('BarcodeDetector' in window)) {
    return;
  }

  $('.barcode-scan').removeClass('d-none');
}

exports.initBarcodeScan = initBarcodeScan;
