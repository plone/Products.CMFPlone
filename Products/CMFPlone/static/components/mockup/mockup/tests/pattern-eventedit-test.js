define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-eventedit'
], function(expect, $, registry, EventEdit) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Event Edit
  ========================== */

  describe('Event Edit', function () {

    afterEach(function() {
      $('body').empty();
    });

    function base_test_case(widgetstring, sel_start, sel_end, sel_open_end, sel_whole_day) {
      // basic test case, which works for different html structures and
      // selectors
      
      var $el = $(widgetstring).appendTo('body');

      registry.scan($el);

      // checking initial
      expect($('.pattern-pickadate-time-wrapper', $el).is(':visible')).to.be.equal(true);
      expect($(sel_end, $el).is(':visible')).to.be.equal(true);
      expect($(sel_start + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('14:00');
      expect($(sel_end + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('15:30');

      // clicking open end
      $(sel_open_end + ' input', $el).prop('checked', true);
      $(sel_open_end + ' input', $el).trigger('change');
      expect($(sel_end, $el).is(':hidden')).to.be.equal(true);
      $(sel_open_end + ' input', $el).prop('checked', false);
      $(sel_open_end + ' input', $el).trigger('change');
      expect($(sel_end, $el).is(':visible')).to.be.equal(true);

      // clicking whole day
      $(sel_whole_day + ' input', $el).prop('checked', true);
      $(sel_whole_day + ' input', $el).trigger('change');
      expect($('.pattern-pickadate-time-wrapper', $el).is(':hidden')).to.be.equal(true);
      $(sel_whole_day + ' input', $el).prop('checked', false);
      $(sel_whole_day + ' input', $el).trigger('change');
      expect($('.pattern-pickadate-time-wrapper', $el).is(':visible')).to.be.equal(true);

      // changing start time
      $(sel_start + ' .pattern-pickadate-time', $el).click();
      $(sel_start + ' .pattern-pickadate-time-wrapper li:contains("10:00 AM")', $el).click();
      expect($(sel_start + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('10:00');
      expect($(sel_end + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('15:30');

      // wrong end time
      $(sel_end + ' .pattern-pickadate-time', $el).click();
      $(sel_end + ' .pattern-pickadate-time-wrapper li:contains("9:00 AM")', $el).click();
      expect($(sel_end, $el).hasClass('error')).to.be.equal(true);
      $(sel_end + ' .pattern-pickadate-time', $el).click();
      $(sel_end + ' .pattern-pickadate-time-wrapper li:contains("10:30 AM")', $el).click();
      expect($(sel_end, $el).hasClass('error')).to.be.equal(false);

      // changing start time again
      $(sel_start + ' .pattern-pickadate-time', $el).click();
      $(sel_start + ' .pattern-pickadate-time-wrapper li:contains("10:00 AM")', $el).click();
      expect($(sel_start + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('10:00');
      expect($(sel_end + ' .pattern-pickadate-time-wrapper input[name="_submit"]', $el).prop('value')).to.be.equal('10:30');
    }

    it('Editing an Dexterity event', function() {

      base_test_case(
        '<div class="pat-eventedit">' +
        '  <div id="formfield-form-widgets-IEventBasic-start">' +
        '    Start' +
        '    <input class="pat-pickadate" type="text" name="form.widgets.IEventBasic.start" value="2014-08-14 14:00" />' +
        '  </div>' +
        '  <div id="formfield-form-widgets-IEventBasic-end">' +
        '    End' +
        '    <input class="pat-pickadate" type="text" name="form.widgets.IEventBasic.end" value="2014-08-14 15:30" />' +
        '  </div>' +
        '  <div id="formfield-form-widgets-IEventBasic-whole_day">' +
        '    Whole Day' +
        '    <input type="checkbox" />' +
        '  </div>' +
        '  <div id="formfield-form-widgets-IEventBasic-open_end">' +
        '    Open End' +
        '    <input type="checkbox" />' +
        '  </div>' +
        '</div>',
        'div#formfield-form-widgets-IEventBasic-start',
        'div#formfield-form-widgets-IEventBasic-end',
        'div#formfield-form-widgets-IEventBasic-open_end',
        'div#formfield-form-widgets-IEventBasic-whole_day'
      );

    });

    it('Editing an Archetypes event', function() {

      base_test_case(
        '<div class="pat-eventedit">' +
        '  <div id="archetypes-fieldname-startDate">' +
        '    Start' +
        '    <input class="pat-pickadate" type="text" name="startDate" value="2014-08-14 14:00" />' +
        '  </div>' +
        '  <div id="archetypes-fieldname-endDate">' +
        '    End' +
        '    <input class="pat-pickadate" type="text" name="endDate" value="2014-08-14 15:30" />' +
        '  </div>' +
        '  <div id="archetypes-fieldname-wholeDay">' +
        '    Whole Day' +
        '    <input type="checkbox" id="wholeDay" />' +
        '  </div>' +
        '  <div id="archetypes-fieldname-openEnd">' +
        '    Open End' +
        '    <input type="checkbox" id="openEnd" />' +
        '  </div>' +
        '</div>',
        'div#archetypes-fieldname-startDate',
        'div#archetypes-fieldname-endDate',
        'div#archetypes-fieldname-openEnd',
        'div#archetypes-fieldname-wholeDay'
      );

    });

  });
});
