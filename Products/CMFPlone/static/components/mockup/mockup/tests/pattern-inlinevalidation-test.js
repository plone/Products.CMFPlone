define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-inlinevalidation'
], function(expect, $, sinon, registry, Pattern) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Inline Validation
   ========================== */

  describe('Inline Validation', function () {
    afterEach(function() {
      $('body').empty();
    });

    it('A z3c.form input is validated on the "blur" event', function() {
      var widget = '<div class="pat-inlinevalidation" data-pat-inlinevalidation=\'{"type": "z3c.form"}\'>' +
        '  <input id="form-widgets-IDublinCore-title"' +
        '         name="form.widgets.IDublinCore.title"' +
        '         class="text-widget required textline-field"' +
        '         value="Welcome to Plone" type="text">' +
        '</div>';
      var $el = $(widget).appendTo('body');
      $.extend(true, Pattern.prototype, {validate_z3cform_field: sinon.spy()});
      var pattern = registry.patterns.inlinevalidation.init($el, null, {type: 'z3c.form'});
      expect(pattern.validate_z3cform_field.called).to.equal(false);
      $el.children('input').blur();
      expect(pattern.validate_z3cform_field.called).to.equal(true);
    });

    it('A formlib input is validated on the "blur" event', function() {
      var $el = $('<div class="pat-inlinevalidation" data-pat-inlinevalidation=\'{"type": "formlib"}\'> <input type="text"> </div>')
                .appendTo('body');
      $.extend(true, Pattern.prototype, {validate_formlib_field: sinon.spy()});
      var pattern = registry.patterns.inlinevalidation.init($el, null, {type: 'formlib'});
      expect(pattern.validate_formlib_field.called).to.equal(false);
      $el.children('input').blur();
      expect(pattern.validate_formlib_field.called).to.equal(true);
    });

    it('An archetypes input is validated on the "blur" event', function() {
      var $el = $('<div class="pat-inlinevalidation" data-pat-inlinevalidation=\'{"type": "archetypes"}\'> <input class="blurrable" type="text"> </div>')
                .appendTo('body');
      $.extend(true, Pattern.prototype, {validate_archetypes_field: sinon.spy()});
      var pattern = registry.patterns.inlinevalidation.init($el, null, {type: 'archetypes'});
      expect(pattern.validate_archetypes_field.called).to.equal(false);
      $el.children('input').blur();
      expect(pattern.validate_archetypes_field.called).to.equal(true);
    });
  });
});
