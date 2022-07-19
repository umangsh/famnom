'use strict';

const constants = require('./constants.js');
const setup = require('./setup.js');

const {test} = QUnit;
QUnit.module('base');
setup.setup();

const base = require(constants.JS_PATH + 'base.js');

test('base.unhideSubmitSpinner', function(assert) {
  assert.true($('#submit_spinner').hasClass('d-none'), 'spinner hidden');
  base.unhideSubmitSpinner();
  assert.false($('#submit_spinner').hasClass('d-none'), 'spinner not hidden');
});
