define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-cookietrigger'
], function(expect, $, sinon, registry, Pattern) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ====================
   TEST: Cookie Trigger 
   ==================== */

  describe('Cookie Trigger', function () {
    afterEach(function() {
      $('body').empty();
    });

    it('The .pat-cookietrigger DOM element is shown if cookies are disabled', function() {
      var widget = 
        '<div class="portalMessage error pat-cookietrigger">' +
        '  Cookies are not enabled. You must enable cookies before you can log in.' +
        '</div>';

      var $el = $(widget).appendTo('body').hide();
      $.extend(true, Pattern.prototype, {isCookiesEnabled: sinon.stub().returns(0)});
      expect($el.is(':visible')).to.equal(false);
      var pattern = registry.patterns.cookietrigger.init($el);
      expect($el.is(':visible')).to.equal(true);
    });

    it('The .pat-cookietrigger DOM element is hidden if cookies are enabled', function() {
      var widget = 
        '<div class="portalMessage error pat-cookietrigger">' +
        '  Cookies are not enabled. You must enable cookies before you can log in.' +
        '</div>';

      var $el = $(widget).appendTo('body').hide();
      $.extend(true, Pattern.prototype, {isCookiesEnabled: sinon.stub().returns(1)});
      expect($el.is(':visible')).to.equal(false);
      var pattern = registry.patterns.cookietrigger.init($el);
      expect($el.is(':visible')).to.equal(false);
    });
  });
});
