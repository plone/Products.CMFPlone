define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-pickadate',
  'mockup-patterns-select2'
], function(expect, $, sinon, registry, PickADate, Select2) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: PickADate
  ========================== */

  describe('PickADate', function() {

    beforeEach(function() {
      this.$el = $('<div><input class="pat-pickadate" /></div>');
      this.clock = sinon.useFakeTimers();
    });

    afterEach(function() {
      $('body').empty();
      this.clock.restore();
    });

    it('date and time element initialized', function() {
      var self = this;

      // pickadate is not initialized
      expect($('.pattern-pickadate-wrapper', self.$el).size()).to.equal(0);

      // scan dom for patterns
      registry.scan(self.$el);

      // pickadate is initialized
      expect($('.pattern-pickadate-wrapper', this.$el).size()).to.equal(1);

      var dateWrapper = $('.pattern-pickadate-date', self.$el).parent(),
          timeWrapper = $('.pattern-pickadate-time', self.$el).parent();

      // main element is hidden
      expect(self.$el.is(':hidden')).to.be.equal(true);

      // date and time inputs are there by default
      expect($('.pattern-pickadate-date', self.$el).size()).to.equal(1);
      expect($('.pattern-pickadate-time', self.$el).size()).to.equal(1);

      // no value on main element
      expect(self.$el.val()).to.be.equal('');

      // no picker is open
      expect(dateWrapper.find('.picker--opened').size()).to.be.equal(0);
      expect(timeWrapper.find('.picker--opened').size()).to.be.equal(0);
    });

    it('open date picker', function(){
      var self = this;
      registry.scan(self.$el);
      var dateWrapper = $('.pattern-pickadate-date', self.$el).parent(),
          timeWrapper = $('.pattern-pickadate-time', self.$el).parent();

      // we open date picker (calendar)
      $('.pattern-pickadate-date', self.$el).click();

      this.clock.tick(1000);
      // date picker should be opened but not time picker
      expect(dateWrapper.find('.picker--opened').size()).to.be.equal(1);
      expect(timeWrapper.find('.picker--opened').size()).to.be.equal(0);

    });

    it('select date from picker', function(){
      var self = this;
      registry.scan(self.$el);
      var dateWrapper = $('.pattern-pickadate-date', self.$el).parent(),
          timeWrapper = $('.pattern-pickadate-time', self.$el).parent();

      // select some date
      $('.pattern-pickadate-date', self.$el).click();
      var $selectedDate = dateWrapper.find('td > div').first().click();

      // selected date should be saved on date picker element
      expect($('.pattern-pickadate-date', self.$el).attr('data-value')).to.be.equal($selectedDate.attr('data-pick'));

      // since time is not selected we still dont expect main element to have
      // value
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');

      // we open time picker
      $('.pattern-pickadate-time', self.$el).click();

      // time picker should be opened but not date picker
      this.clock.tick(1000);
      expect(dateWrapper.find('.picker--opened').size()).to.be.equal(0);
      expect(timeWrapper.find('.picker--opened').size()).to.be.equal(1);

      // select some time
      var $selectedTime = timeWrapper.find('li').first().next().click();

      // selected time should be saved on time picker element
      expect($('.pattern-pickadate-time', self.$el).attr('data-value')).to.be.equal($selectedTime.attr('data-pick'));

      // main element should now have value
      expect($('.pat-pickadate', self.$el).val()).to.not.equal('');

      // clearing time ...
      $('.pattern-pickadate-time', self.$el).click();
      this.clock.tick(1000);
      $('.picker__button--clear', timeWrapper).click();

      // ... should remove value from main element
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');

      // select time again
      $selectedTime = timeWrapper.find('li').first().next().click();

      // main element should now have again value
      expect($('.pat-pickadate', self.$el).val()).to.not.equal('');

      // clearing date ...
      $('.pattern-pickadate-date', self.$el).click();
      $('.pattern-pickadate-date', self.$el).click();
      $('.picker__button--clear', dateWrapper).click();

      // ... should also remove value from main element
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');

      // selecting time again ...
      $selectedTime = timeWrapper.find('li').first().next().click();

      // ... should still keep main element value empty since date picker is
      // cleared
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');

    });

    it('date and time element have custom separator', function() {
      var self = this;

      $('.pat-pickadate', self.$el).attr('data-pat-pickadate', 'separator:===');

      // scan dom for patterns
      registry.scan(self.$el);

      expect($('.pattern-pickadate-separator', self.$el).text()).to.be.equal('===');
    });

    it('date and time picker except custom settings', function() {
      var self = this;

      // custom settings for date and time widget
      $('.pat-pickadate', self.$el).attr(
        'data-pat-pickadate',
        JSON.stringify({
          date: {
            selectYears: false,
            selectMonths: false
          },
          time: {
            interval: 60
          }
        })
      );

      // scan dom for patterns
      registry.scan(self.$el);

      // there are not dropdowns to select year or month
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--year').size()).to.be.equal(0);
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--month').size()).to.be.equal(0);

      // there should be 25 items in time picker list. 24 for each hour and one
      // to for clear button
      expect($('.pattern-pickadate-time', self.$el).parent().find('li').size()).to.be.equal(25);
    });

    it('only date element', function() {
      var self = this;

      // add option which disables time picker
      $('.pat-pickadate', self.$el).attr('data-pat-pickadate', 'time:false');

      // pickadate is not initialized
      expect($('.pattern-pickadate-wrapper', self.$el).size()).to.equal(0);

      // scan dom for patterns
      registry.scan(self.$el);

      // pickadate is initialized
      expect($('.pattern-pickadate-wrapper', self.$el).size()).to.equal(1);

      var dateWrapper = $('.pattern-pickadate-date', self.$el).parent();

      // main element is hidden
      expect(self.$el.is(':hidden')).to.be.equal(true);

      // date input is there by default
      expect($('.pattern-pickadate-date', self.$el).size()).to.equal(1);
      expect($('.pattern-pickadate-time', self.$el).size()).to.equal(0);

      // no value on main element
      expect(self.$el.val()).to.be.equal('');

      // date picker is not open
      expect(dateWrapper.find('.picker--opened').size()).to.be.equal(0);

      // we open date picker (calendar)
      $('.pattern-pickadate-date', self.$el).click();

      // date picker should be opened
      this.clock.tick(1000);
      expect(dateWrapper.find('.picker--opened').size()).to.be.equal(1);

      // select some date
      var $selectedDate = dateWrapper.find('td > div').first().click();

      // selected date should be saved on date picker element
      expect($('.pattern-pickadate-date', self.$el).attr('data-value')).to.be.equal($selectedDate.attr('data-pick'));

      // and also on main element since time element is disabled
      expect($('.pat-pickadate', self.$el).val()).to.not.equal('');

      // clearing date ...
      $('.pattern-pickadate-date', self.$el).click();
      $('.pattern-pickadate-date', self.$el).click();
      this.clock.tick(1000);
      $('.picker__button--clear', dateWrapper).click();

      // ... should also remove value from main element
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');
    });

    it('only time element', function() {
      var self = this;

      // add option which disables date picker
      $('.pat-pickadate', self.$el).attr('data-pat-pickadate', 'date:false');

      // pickadate is not initialized
      expect($('.pattern-pickadate-wrapper', self.$el).size()).to.equal(0);

      // scan dom for patterns
      registry.scan(self.$el);

      // pickadate is initialized
      expect($('.pattern-pickadate-wrapper', self.$el).size()).to.equal(1);

      var timeWrapper = $('.pattern-pickadate-time', self.$el).parent();

      // main element is hidden
      expect(self.$el.is(':hidden')).to.be.equal(true);

      // time input is there by default
      expect($('.pattern-pickadate-date', self.$el).size()).to.equal(0);
      expect($('.pattern-pickadate-time', self.$el).size()).to.equal(1);

      // no value on main element
      expect(self.$el.val()).to.be.equal('');

      // time picker is not open
      expect(timeWrapper.find('.picker--opened').size()).to.be.equal(0);

      // we open time picker (calendar)
      $('.pattern-pickadate-time', self.$el).click();

      // time picker should be opened
      this.clock.tick(1000);
      expect(timeWrapper.find('.picker--opened').size()).to.be.equal(1);

      // select some time
      var $selectedTime = timeWrapper.find('li').first().next().click();

      // selected date should be saved on date picker element
      expect($('.pattern-pickadate-time', self.$el).attr('data-value')).to.be.equal($selectedTime.attr('data-pick'));

      // and also on main element since time element is disabled
      expect($('.pat-pickadate', self.$el).val()).to.not.equal('');

      // clearing date ...
      $('.pattern-pickadate-time', self.$el).click();
      this.clock.tick(1000);
      $('.picker__button--clear', timeWrapper).click();

      // ... should also remove value from main element
      expect($('.pat-pickadate', self.$el).val()).to.be.equal('');
    });

    it('populating date and time picker', function() {
      var self = this;

      // custom settings for date and time widget
      $('.pat-pickadate', self.$el).attr('value', '2001-10-10 10:10');

      // scan dom for patterns
      registry.scan(self.$el);

      // date picker value is parsed correctly from main element ...
      expect($('.pattern-pickadate-date', self.$el).attr('data-value')).to.be.equal('2001-10-10');

      // ... and make sure 2001-10-10 is picked in the date picker calendar
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--year > :selected').val()).to.be.equal('2001');
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--month > :selected').val()).to.be.equal('9');
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__day--selected').text()).to.be.equal('10');

      // time picker value is parsed correctly from main element
      expect($('.pattern-pickadate-time', self.$el).attr('data-value')).to.be.equal('10:10');

      // and make sure 10:00 AM is picked in the time picker list
      expect($('.pattern-pickadate-time', self.$el).parent().find('.picker__list-item--selected').attr('data-pick')).to.be.equal('630');

    });

    it('populating only time picker', function() {
      var self = this;

      // custom settings for date and time widget
      $('.pat-pickadate', self.$el)
        .attr('value', '15:10')
        .attr('data-pat-pickadate', 'date:false');

      // scan dom for patterns
      registry.scan(self.$el);

      // time picker value is parsed correctly from main element
      expect($('.pattern-pickadate-time', self.$el).attr('data-value')).to.be.equal('15:10');

      // and make sure 10:00 AM is picked in the time picker list
      expect($('.pattern-pickadate-time', self.$el).parent().find('.picker__list-item--selected').attr('data-pick')).to.be.equal('930');

    });

    it('populating only date picker', function() {
      var self = this;

      // custom settings for date and time widget
      $('.pat-pickadate', self.$el)
        .attr('value', '1801-12-30')
        .attr('data-pat-pickadate', 'time:false');

      // scan dom for patterns
      registry.scan(self.$el);

      // date picker value is parsed correctly from main element ...
      expect($('.pattern-pickadate-date', self.$el).attr('data-value')).to.be.equal('1801-12-30');

      // ... and make sure 1801-12-30 is picked in the date picker calendar
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--year > :selected').val()).to.be.equal('1801');
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__select--month > :selected').val()).to.be.equal('11');
      expect($('.pattern-pickadate-date', self.$el).parent().find('.picker__day--selected').text()).to.be.equal('30');

    });

    it('getting around bug in pickatime when selecting 00:00', function() {
      var self = this;

      // custom settings for time widget
      $('.pat-pickadate', self.$el)
        .attr('value', '00:00')
        .attr('data-pat-pickadate', 'date:false');

      registry.scan(self.$el);

      // time picker value is parsed correctly from main element
      expect($('.pattern-pickadate-time', self.$el).attr('data-value')).to.be.equal('00:00');

      // and make sure 10:00 AM is picked in the time picker list
      expect($('.pattern-pickadate-time', self.$el).parent().find('.picker__list-item--selected').attr('data-pick')).to.be.equal('0');

    });

    describe('PickADate with timezone', function() {
      it('has date, time and timezone', function() {
        var self = this,
            $input = $('.pat-pickadate', self.$el)
              .attr('data-pat-pickadate', '{"timezone": {"data": [' +
                                            '{"id":"Europe/Berlin","text":"Europe/Berlin"},' +
                                            '{"id":"Europe/Vienna","text":"Europe/Vienna"}' +
                                          ']}}'
              );
        self.$el.appendTo('body');
        registry.scan($input);

        // date and time should exist by default
        var $timeWrapper = $('.pattern-pickadate-time-wrapper', self.$el),
            $dateWrapper = $('.pattern-pickadate-date-wrapper', self.$el);
        expect($timeWrapper.size()).to.equal(1);
        expect($dateWrapper.size()).to.equal(1);

        // timezone elements should not be available
        var $results = $('li.select2-result-selectable');
        expect($results.size()).to.equal(0);

        var $pattern = $('input.pattern-pickadate-timezone.select2-offscreen');
        $pattern.on('select2-open', function() {
          // timezone elements should be available
          $results = $('li.select2-result-selectable');
          expect($results.size()).to.equal(2);
        });
        $('a.select2-choice').trigger('mousedown');

        // value of main element should be empty
        expect($('.pat-pickadate').val()).to.equal('');

        // after changing timezone the value should still be empty
        $pattern.select2('val', 'Europe/Berlin', { triggerChange: true });
        expect($pattern.val()).to.equal('Europe/Berlin');
        expect($input.val()).to.equal('');

        // set date and time and check if value of main element gets timezone
        $('.pattern-pickadate-date', self.$el).click();
        var $selectedDate = $dateWrapper.find('td > div').first().click();
        expect($input.val()).to.equal('');
        $('.pattern-pickadate-time', self.$el).click();
        var $selectedTime = $timeWrapper.find('li').first().next().click();
        expect($input.val()).to.equal($('input:last', $dateWrapper).val() + ' ' + $('input:last', $timeWrapper).val() + ' ' + 'Europe/Berlin');

        // change timezone to second value and check if value of main element changes
        $pattern.select2('val', 'Europe/Vienna', { triggerChange: true });
        expect($pattern.val()).to.equal('Europe/Vienna');
        expect($input.val()).to.equal($('input:last', $dateWrapper).val() + ' ' + $('input:last', $timeWrapper).val() + ' ' + 'Europe/Vienna');
      });

      it('should take the default timezone when it is set', function() {
        var self = this,
            $input = $('.pat-pickadate', self.$el)
              .attr('data-pat-pickadate', '{"timezone": {"default": "Europe/Vienna", "data": [' +
                                            '{"id":"Europe/Berlin","text":"Europe/Berlin"},' +
                                            '{"id":"Europe/Vienna","text":"Europe/Vienna"},' +
                                            '{"id":"Europe/Madrid","text":"Europe/Madrid"}' +
                                          ']}}'
              );
        self.$el.appendTo('body');
        registry.scan($input);

        // check if data values are set to default
        expect($('.pattern-pickadate-timezone .select2-chosen').text()).to.equal('Europe/Vienna');
        expect($('input.pattern-pickadate-timezone.select2-offscreen').attr('data-value')).to.equal('Europe/Vienna');

      });

      it('should only set the default value when it exists in the list', function() {
        var self = this,
            $input = $('.pat-pickadate', self.$el)
              .attr('data-pat-pickadate', '{"timezone": {"default": "Europe/Madrid", "data": [' +
                                            '{"id":"Europe/Berlin","text":"Europe/Berlin"},' +
                                            '{"id":"Europe/Vienna","text":"Europe/Vienna"}' +
                                          ']}}'
              );
        self.$el.appendTo('body');
        registry.scan($input, ['pickadate']);

        // check if visible and data value are set to default
        expect($('.pattern-pickadate-timezone .select2-chosen').text()).to.equal('Enter timezone...');
        expect($('input.pattern-pickadate-timezone.select2-offscreen').attr('data-value')).to.equal(undefined);

      });

      it('should write to default and disable the dropdown field if only one value exists', function() {
        var self = this,
            $input = $('.pat-pickadate', self.$el)
              .attr('data-pat-pickadate', '{"timezone": {"data": [' +
                                            '{"id":"Europe/Berlin","text":"Europe/Berlin"}' +
                                          ']}}'
              );
        self.$el.appendTo('body');
        registry.scan($input, ['pickadate']);

        var $time = $('.pattern-pickadate-timezone');

        // check if data values are set to default
        expect($('.select2-chosen', $time).text()).to.equal('Europe/Berlin');
        expect($('input.pattern-pickadate-timezone.select2-offscreen').attr('data-value')).to.equal('Europe/Berlin');

        expect($('.pattern-pickadate-timezone').data('select2')._enabled).to.equal(false);
        expect($('.select2-container-disabled').size()).to.equal(1);
      });

    });

  });

});
