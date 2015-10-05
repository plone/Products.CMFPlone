define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-passwordstrength'
], function(expect, $, registry, PasswordStrength) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: Password strength
   ========================== */

  describe('Password strength', function () {

    var orig_setTimeout = window.setTimeout;

    function fakeZxcvbn(input, strings) {
        window.providedStrings = strings;
        return {
            score: Math.min(input.length, 4)
        };
    }

    function getScripts() {
        return [].map.call(
            document.getElementsByTagName('script'),
            function (s) { return s.src; }
        ).filter(function (src) { return src.indexOf('zxcvbn') !== -1; });
    }

    beforeEach(function() {
        window.setTimeout = function (fun, interval) {
            window.providedInterval = interval;
            fun();
            return 0;
        };
    });

    afterEach(function() {
      window.setTimeout = orig_setTimeout;
    });

    it('adds markup below input element', function() {
      var $el = $('<div><input type="password" class="pat-passwordstrength" /></div>');
      window.zxcvbn = fakeZxcvbn;
      registry.scan($el);

      expect($el.find('.pat-passwordstrength').size()).to.be.equal(1);
      expect($el.find('.pat-passwordstrength-meter').hasClass('level-0')).to.be.equal(true);
    });

    it('tries to load zxcvbn once if not available', function() {
      var $el2, $el = $('<div><input type="password" class="pat-passwordstrength" data-pat-passwordstrength="zxcvbn: http://example.com/zxcvbn.js" /></div>');
      window.zxcvbn = undefined;
      expect(getScripts().length).to.equal(0);
      registry.scan($el);
      expect(getScripts().length).to.equal(1);
      expect(getScripts()).to.contain('http://example.com/zxcvbn.js');

      $el.find('input[type=password]').attr('value', 'a').trigger('keyup');
      expect(getScripts().length).to.equal(1);
      $el.find('input[type=password]').attr('value', 'aa').trigger('keyup');
      expect(getScripts().length).to.equal(1);
      $el.find('input[type=password]').attr('value', 'aaa').trigger('keyup');
      expect(getScripts().length).to.equal(1);
      expect(getScripts()).to.contain('http://example.com/zxcvbn.js');

      $el2 = $('<div><input type="password" class="pat-passwordstrength" data-pat-passwordstrength="zxcvbn: http://example.com/zxcvbn.js" /></div>');
      registry.scan($el2);
      expect(getScripts().length).to.equal(1);
      expect(getScripts()).to.contain('http://example.com/zxcvbn.js');
    });

    it('sets level based on the entered password', function() {
      var $el = $('<div><input type="password" class="pat-passwordstrength" /></div>');
      window.zxcvbn = fakeZxcvbn;
      registry.scan($el);

      $el.find('input[type=password]').attr('value', 'a').trigger('keyup');
      expect($el.find('.pat-passwordstrength-meter').attr('class')).to.equal(
          "pat-passwordstrength-meter level-1");
      expect(window.providedStrings.length).to.equal(0);
      expect(window.providedInterval).to.equal(500);

      $el.find('input[type=password]').attr('value', 'aa').trigger('keyup');
      expect($el.find('.pat-passwordstrength-meter').attr('class')).to.equal(
          "pat-passwordstrength-meter level-2");
      expect(window.providedStrings.length).to.equal(0);
      expect(window.providedInterval).to.equal(500);
    });

    it('provides zxcvbn with other form field values', function() {
      var $el = $('<form>' +
                  '<input type="input" name="username" value="bob_geldof" />' +
                  '<input type="password" class="pat-passwordstrength" />' +
                  '<input type="checkbox" name="spam_me" checked="yes">' +
                  '</form>');
      window.zxcvbn = fakeZxcvbn;
      registry.scan($el);

      $el.find('input[type=password]').attr('value', 'a').trigger('keyup');
      expect($el.find('.pat-passwordstrength-meter').attr('class')).to.equal(
          "pat-passwordstrength-meter level-1");
      expect(window.providedStrings.length).to.equal(2);
      expect(window.providedStrings).to.contain('bob_geldof');
      expect(window.providedStrings).to.contain('on');
    });
  });
});
