define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-tooltip'
], function(expect, $, registry, Tooltip) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Tooltip
  ========================== */

  describe('Tooltip', function () {

    beforeEach(function() {
      this.$el = $('' +
        '<div><a href="#" class="pat-tooltip" data-toggle="tooltip" title="data">' +
        '  Hover over this line to see a tooltip' +
        '</a></div>');
      $('body').append(this.$el);
    });

    afterEach(function() {
      this.$el.remove();
    });


    it.skip('tooltip appears and disappears', function() {
      registry.scan(this.$el);

      var trs;

      var $el = this.$el.find('a');
      $el.data('suppress.mouseenter', (new Date().getTime()) + 10000);
      $el.trigger('mouseenter');
      trs = this.$el.find('.tooltip');
      expect(trs.eq(0).length).to.equal(1);

      this.$el.trigger('mouseleave');
      trs = this.$el.find('.tooltip');
      expect(trs.eq(0).length).to.equal(0);
    });

  });
});
