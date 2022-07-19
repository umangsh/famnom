'use strict';

const constants = require('./constants.js');

const {test} = QUnit;
QUnit.module('data_loader');

const dataLoader = require(constants.JS_PATH + 'data_loader.js');

test('data_loader.getNutrients.element_missing', function(assert) {
  dataLoader.getNutrients($('#element_not_present'), true);
  assert.true($('#nutrition-label').attr('data-1') === undefined,
      'missing element, no data loaded.');
});

test('data_loader.getNutrients.success', function(assert) {
  const done = assert.async();

  $.mockjax({
    url: '/my_nutrient_ajax/ID1/',
    contentType: 'application/json',
    responseText: [
      {
        'nutrient_id': 1,
        'amount': 5.0,
      },
    ],
  });

  dataLoader.getNutrients($('#nutrition-label-inner'), false, function() {
    assert.true($('#nutrition-label').attr('data-1') == 5.0,
        'call successful, nutrient info loaded.');
    done();
  });
});

test('data_loader.getServings.success', function(assert) {
  const done = assert.async();

  assert.true($('#abc-serving option').length == 0, 'servings empty.');

  $.mockjax({
    url: '/my_serving_ajax/ID1/',
    contentType: 'application/json',
    responseText: [
      [
        'ID2',
        {
          'label': 'Serving1',
          'data-gm-wt': 10,
          'data-wt-unit': 'g',
        },
      ],
    ],
  });

  dataLoader.getServings($('#abc-child_external_id'), function() {
    assert.true($('#abc-serving option').length == 1,
        'call successful, serving info loaded.');
    done();
  });
});

test('data_loader.checkbarcodeexists.success', function(assert) {
  const done = assert.async();

  assert.true($('#gtin_upc_message').hasClass('d-none'),
      'upc redirect message hidden');

  $.mockjax({
    url: '/my_barcode_ajax/UPC/',
    contentType: 'application/json',
    responseText: {
      'url': 'sample_url',
    },
  });

  dataLoader.checkbarcodeexists(function() {
    assert.false($('#gtin_upc_message').hasClass('d-none'),
        'upc redirect message not hidden');
    done();
  });
});

test('data_loader.getTopFoodsHTML.success', function(assert) {
  const done = assert.async();

  assert.true($('.top-foods-parent').children().length == 0, 'top foods empty');

  $.mockjax({
    url: '/top_foods_ajax/1/',
    contentType: 'application/html',
    responseText: '<h1>Test Page</h1>',
  });

  dataLoader.getTopFoodsHTML(1, function() {
    assert.true($('.top-foods-parent').children().length == 1,
        'top foods rendered');
    assert.equal($('.top-foods-parent h1').text(), 'Test Page',
        'html strings validated.');
    assert.true($('.top-foods-spinner').is(':hidden'),
        'top foods spinner hidden');
    done();
  });
});

test('data_loader.getRecentFoodsHTML.success', function(assert) {
  const done = assert.async();

  assert.true($('.recent-foods-parent').children().length == 0,
      'recent foods empty');

  $.mockjax({
    url: '/my_recent_foods_ajax/1/',
    contentType: 'application/html',
    responseText: '<h1>Test Page</h1>',
  });

  dataLoader.getRecentFoodsHTML(1, function() {
    assert.true($('.recent-foods-parent').children().length == 1,
        'top foods rendered');
    assert.equal($('.recent-foods-parent h1').text(), 'Test Page',
        'html strings validated.');
    assert.true($('.recent-foods-spinner').is(':hidden'),
        'top foods spinner hidden');
    done();
  });
});

test('data_loader.getAvailableFoodsHTML.success', function(assert) {
  const done = assert.async();

  assert.true($('.available-foods-parent').children().length == 0,
      'available foods empty');

  $.mockjax({
    url: '/my_available_foods_ajax/1/',
    contentType: 'application/html',
    responseText: '<h1>Test Page</h1>',
  });

  dataLoader.getAvailableFoodsHTML(1, function() {
    assert.true($('.available-foods-parent').children().length == 1,
        'available foods rendered');
    assert.equal($('.available-foods-parent h1').text(), 'Test Page',
        'html strings validated.');
    assert.true($('.available-foods-spinner').is(':hidden'),
        'available foods spinner hidden');
    done();
  });
});

test('data_loader.getTrackerHTML.success', function(assert) {
  const done = assert.async();

  assert.true($('.tracker-parent').children().length == 0, 'tracker empty');

  $.mockjax({
    url: '/my_tracker_ajax/1/',
    contentType: 'application/html',
    responseText: '<h1>Test Page</h1>',
  });

  dataLoader.getTrackerHTML(1, function() {
    assert.true($('.tracker-parent').children().length == 1,
        'tracker rendered');
    assert.equal($('.tracker-parent h1').text(), 'Test Page',
        'html strings validated.');
    assert.true($('.tracker-spinner').is(':hidden'),
        'tracker spinner hidden');
    done();
  });
});

test('data_loader.getSuggestedFoodsHTML.success', function(assert) {
  const done = assert.async();

  assert.true($('.suggested-foods-parent').children().length == 0,
      'suggested foods empty');

  $.mockjax({
    url: '/my_suggested_foods_ajax/',
    contentType: 'application/html',
    responseText: '<h1>Test Page</h1>',
  });

  dataLoader.getSuggestedFoodsHTML(function() {
    assert.true($('.suggested-foods-parent').children().length == 1,
        'suggested foods rendered');
    assert.equal($('.suggested-foods-parent h1').text(), 'Test Page',
        'html strings validated.');
    assert.true($('.suggested-foods-spinner').is(':hidden'),
        'suggested foods spinner hidden');
    done();
  });
});
