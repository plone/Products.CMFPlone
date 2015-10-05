define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-formautofocus'
], function(expect, $, registry, FormAutoFocus) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: FormAutoFocus
  ========================== */

  describe('FormAutoFocus', function() {
    beforeEach(function() {
      // We are including another form to the DOM, just to be sure we focus
      // inside the form that actually has the pattern
      this.$el = $('' +
        '<div>' +
        ' <form>' +
        '  <input value="" id="first-input-should-not-focus"/>' +
        '  <div class="error">' +
        '    <input value="" id="input-inside-error-should-not-focus" />' +
        '  </div>' +
        ' </form>' +
        '</div>')
        .appendTo('body');
    });
    afterEach(function() {
      this.$el.remove();
    });
    it('when the condition is met, focus on the first one', function(done) {
      var $el = $('' +
        '<div>' +
        ' <form class="pat-formautofocus">' +
        '  <input value="" id="first-input"/>' +
        '  <div class="error">' +
        '    <input value="" id="input1-inside-error" />' +
        '  </div>' +
        '  <div class="error">' +
        '    <input value="" id="input2-inside-error" />' +
        '  </div>' +
        ' </form>' +
        '</div>')
        .appendTo('body');
      expect($('input#first-input').is(':focus')).to.be.equal(false);
      $('input').on('focusin', function() {
        expect($(this).attr('id')).to.equal('input1-inside-error');
        expect($('input#first-input-should-not-focus').is(':focus')).to.be.equal(false);
        expect($('input#input-inside-error-should-not-focus').is(':focus')).to.be.equal(false);
        done();
      });
      registry.scan($el);
      $el.remove();
    });

    it('when the condition is not met, focus on the first input', function(done) {
      var $el = $('' +
        '<div>' +
        ' <form class="pat-formautofocus">' +
        '  <input value="" id="first-input"/>' +
        '  <input value="" id="second-input"/>' +
        ' </form>' +
        '</div>')
        .appendTo('body');
      expect($('input#first-input').is(':focus')).to.be.equal(false);
      $('input').on('focusin', function() {
        expect($(this).attr('id')).to.equal('first-input');
        expect($('input#first-input-should-not-focus').is(':focus')).to.be.equal(false);
        expect($('input#input-inside-error-should-not-focus').is(':focus')).to.be.equal(false);
        done();
      });
      registry.scan($el);
      $el.remove();
    });
  });
});
