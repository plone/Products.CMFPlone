define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-moment'
], function(expect, $, registry, Moment) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Moment
  ========================== */

  describe('Moment', function () {
    beforeEach(function() {
    });
    it('test parse relative', function() {
      var date = new Date();
      date.setMinutes(date.getMinutes() + 2);
      var $el = $('<div class="pat-moment" data-pat-moment="format:relative">' + date + '</div>');
      registry.scan($el);
      expect($el.html()).to.equal('in 2 minutes');
    });
    it('test parse calendar', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:calendar">2012-10-02 14:30</div>');
      registry.scan($el);
      expect($el.html()).to.equal('10/02/2012');
    });
    it('test parse custom', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:YYYY">2012-10-02 14:30</div>');
      registry.scan($el);
      expect($el.html()).to.equal('2012');
    });
    it('test parse custom', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:YYYY;selector:*"><div>2012-10-02 14:30</div></div>');
      registry.scan($el);
      expect($el.find('div').html()).to.equal('2012');
    });
    it('test parse no date', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:calendar"><div></div></div>');
      registry.scan($el);
      expect($el.find('div').html()).to.equal('');
    });
    it('test setTitle true', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:relative;setTitle:true">2012-10-02 14:30</div>');
      registry.scan($el);
      expect($el.attr('title')).to.equal('October 2nd 2012, 2:30:00 pm');
    });
    it('test setTitle default (false)', function() {
      var $el = $('<div class="pat-moment" data-pat-moment="format:relative">2012-10-02 14:30</div>');
      registry.scan($el);
      expect($el.attr('title')).to.equal(undefined);
    });

  });
});
