/**
 * Initializes the base js.
 */
$(document).ready(function() {
  // Initialize user's timezone
  initTimezone();

  // Initialize all tooltips on the page
  initTooltips();

  // Init addToKitchen button.
  initAddToKitchen();

  // Initialize meal datepickers for log pages.
  initEditDatepicker('#id_meal_date');

  // Initialize datepickers for profile pages.
  initEditDatepicker('#id_date_of_birth', changeMonth=true, changeYear=true);

  // Initialize search autocomplete.
  initSearchAutocomplete();

  // Initialize barcode scan.
  initBarcodeScan();
});

/**
 * Show spinner when submitting a form.
 */
function unhideSubmitSpinner() { // eslint-disable-line no-unused-vars
  $('#submit_spinner').removeClass('d-none');
}

/**
 * Read barcode for search/food creation using camera.
 *
 * @param {HTMLElement} elem The dropdown element.
 */
async function readBarcode(elem) { // eslint-disable-line no-unused-vars
  $('#barcodeModal').modal({
    keyboard: false,
  });

  const stream = await navigator.mediaDevices.getUserMedia({
    video: {
      facingMode: {ideal: 'environment'},
    },
    audio: false,
  });

  $('#barcodeModal').on('hidden.bs.modal', function(e) {
    stream.getTracks().forEach(function(track) {
      track.stop();
    });
  });

  // Get video from camera
  const videoEl = document.querySelector('#barcode-stream');
  videoEl.srcObject = stream;
  await videoEl.play();

  // Read Barcode
  const barcodeDetector = new BarcodeDetector({
    formats: [
      'ean_13',
      'ean_8',
      'upc_a',
      'upc_e',
    ]});

  window.setInterval(async () => {
    const barcodes = await barcodeDetector.detect(videoEl);
    if (barcodes.length <= 0) {
      return;
    }

    $(elem).parent().siblings('input').val(barcodes[0].rawValue);
    $('#barcodeModal').modal('hide');

    // Trigger field change or form submit
    if ($(elem).parent().hasClass('barcode-scan-search')) {
      $(elem).parent().parent().parent().trigger('submit');
    }

    if ($(elem).parent().hasClass('barcode-scan-field')) {
      $(elem).parent().siblings('input').trigger('change');
    }
  }, 1000);
}

exports.unhideSubmitSpinner = unhideSubmitSpinner;
exports.readBarcode = readBarcode;
