define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-sortable'
], function(expect, $, registry, Sortable) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: Toggle
  ========================== */

  describe('Sortable', function() {
    beforeEach(function() {
      this.$el = $('' +
        '<ul class="pat-sortable">' +
          '<li>One</li>' +
          '<li>Two</li>' +
          '<li>Three</li>' +
        '</ul>'
      ).appendTo('body');
    });

    afterEach(function() {
      this.$el.remove();
    });

    it('adds class on drag start', function() {
      var sortable = new Sortable(this.$el);
      var $todrag = this.$el.find('li').eq(0);
      $todrag.trigger('dragstart');
      expect($todrag.hasClass(sortable.options.dragClass)).to.equal(true);
    });

  });

});
