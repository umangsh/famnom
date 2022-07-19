const jsdom = require('jsdom');

/**
 * Setup environment for js tests.
 */
function setup() {
  const html = `
  <!doctype html>
  <html>
    <head></head>
    <body>
      <div id="qunit"></div>
      <div id="qunit-fixture">
        <div id="submit_spinner" class="d-none"></div>
        <div id="nutrition-label">
          <input id="nutrition-label-inner" value="ID1">
        </div>
        <div id="nutrition-servings">
          <input id="abc-child_external_id" value="ID1">
          <input id="abc-quantity">
          <select id="abc-serving"></select>
        </div>
        <div id="nutrition-upc">
          <input id="id_gtin_upc" value="UPC">
          <div id="gtin_upc_message" class="d-none"></div>
        </div>
        <div id="top-foods">
          <div class="top-foods-parent"></div>
          <div class="top-foods-spinner"></div>
        <div>
        <div id="recent-foods">
          <div class="recent-foods-parent"></div>
          <div class="recent-foods-spinner"></div>
        <div>
        <div id="available-foods">
          <div class="available-foods-parent"></div>
          <div class="available-foods-spinner"></div>
        <div>
        <div id="tracker">
          <div class="tracker-parent"></div>
          <div class="tracker-spinner"></div>
        <div>
        <div id="suggested-foods">
          <div class="suggested-foods-parent"></div>
          <div class="suggested-foods-spinner"></div>
        <div>
        <div id="barcode">
          <div class="barcode-scan d-none"></div>
        </div>
      </div>
    </body>
  </html>`;

  const {JSDOM} = jsdom;
  const dom = new JSDOM(html);
  global.window = dom.window;
  global.document = dom.window.document;
  global.$ = global.jQuery = require('jquery');
  require('jquery-mockjax')(global.$, global.window);
  require('bootstrap');
}

exports.setup = setup;
