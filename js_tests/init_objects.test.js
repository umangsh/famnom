'use strict';

const constants = require('./constants.js');

const {test} = QUnit;
QUnit.module('init_objects');

const initObjects = require(constants.JS_PATH + 'init_objects.js');

test('init_objects.initBarcodeScan.unsupported_browser', function(assert) {
  assert.true($('.barcode-scan').hasClass('d-none'),
      'barcode scan hidden before');
  initObjects.initBarcodeScan();
  assert.true($('.barcode-scan').hasClass('d-none'),
      'barcode scan hidden after');
});

test('init_objects.initBarcodeScan.supported_browser', function(assert) {
  assert.true($('.barcode-scan').hasClass('d-none'),
      'barcode scan hidden before');
  global.window.BarcodeDetector = true;
  initObjects.initBarcodeScan();
  assert.false($('.barcode-scan').hasClass('d-none'),
      'barcode scan shown after');
});
