define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-preventdoublesubmit'
], function(expect, $, registry, PreventDoubleSubmit) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: PreventDoubleSubmit
  ========================== */

  describe('PreventDoubleSubmit', function() {
    beforeEach(function() {
      var self = this;
      // mock up `_confirm` func
      self._oldConfirm = PreventDoubleSubmit.prototype._confirm;
      PreventDoubleSubmit.prototype._confirm = function() {
        this.confirmed = true;
      };
    });
    afterEach(function() {
      PreventDoubleSubmit.prototype._confirm = this._oldConfirm;
    });
    it('prevent form to be submitted twice', function() {
      var $el = $('' +
        '<form id="helped" class="pat-preventdoublesubmit">' +
        ' <input type="text" value="Yellow" />' +
        ' <select name="aselect">' +
        '    <option value="1">1</option>' +
        '    <option value="2">2</option>' +
        '</select>' +
        ' <input id="b1" type="submit" value="Submit 1" />' +
        ' <input id="b2" type="submit" class="allowMultiSubmit" value="Submit 2" />' +
        '</form>').on('submit', function(e) { e.preventDefault(); });
      registry.scan($el);

      var guardKlass = 'submitting';
      var optOutKlass = 'allowMultiSubmit';
      var getConfirmed = function(el) {
        return el.data('pattern-preventdoublesubmit').confirmed;
      };
      var resetConfirmed = function(el) {
        el.data('pattern-preventdoublesubmit').confirmed = undefined;
      };

      var $b1 = $('#b1', $el);
      var $b2 = $('#b2', $el);

      expect(getConfirmed($el)).to.be.equal(undefined);
      $b1.trigger('click');
      expect(getConfirmed($el)).to.be.equal(undefined);
      expect($b1.hasClass(guardKlass)).to.be.equal(true);
      $b1.trigger('click');
      expect(getConfirmed($el)).to.be.equal(true);

      // reset confirmed flag
      resetConfirmed($el);

      $b2.trigger('click');
      expect($b2.hasClass(guardKlass)).to.be.equal(true);
      expect(getConfirmed($el)).to.be.equal(undefined);

    });
  });

});
