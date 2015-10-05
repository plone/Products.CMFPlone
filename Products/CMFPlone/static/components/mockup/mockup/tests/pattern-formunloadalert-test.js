define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-formunloadalert'
], function(expect, $, registry, FormUnloadAlert) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: FormUnloadAlert
  ========================== */

  describe('FormUnloadAlert', function() {
    beforeEach(function() {
      this.$el = $('' +
        '<form class="pat-formunloadalert">' +
        ' <select name="aselect">' +
        '    <option value="1">1</option>' +
        '    <option value="2">2</option>' +
        '</select>' +
        '<input id="b1" type="submit" value="Submit" />' +
        '<a href="patterns.html">Click here to go somewhere else</a>' +
        '</form>');
    });
    afterEach(function() {
      var pattern = this.$el.data('pattern-formunloadalert');
      pattern._changed = false;
    });
    it('prevent unload of form with changes', function(done) {
      registry.scan(this.$el);

      // current instance of the pattern
      var pattern = this.$el.data('pattern-formunloadalert');
      var $select = $('select', this.$el);

      expect(pattern._changed).to.be.equal(false);

      $select.trigger('change');
      expect(pattern._changed).to.be.equal(true);

      $('a', this.$el)
        .on('click', function(e) {
          var returnedString = pattern._handleUnload(pattern, e);
          var returnValue = e.returnValue;
          if (e.returnValue === undefined) {
            // If we are testing in a Safari based browser, e.g. PhantomJS
            // then e.returnValue is not set, it just reads the string for
            // dialog message
            returnValue = returnedString;
          }
          expect(returnValue).to.equal(pattern.options.message);
          // Need to stop the propagation of this event otherwise
          // we get stuck in a loop.
          e.stopPropagation();
          done();
        });
      $('a', this.$el).trigger('click');
    });
    it('do not show message if submitting', function(done) {
      registry.scan(this.$el);

      // current instance of the pattern
      var pattern = this.$el.data('pattern-formunloadalert');
      var $select = $('select', this.$el);

      expect(pattern._changed).to.be.equal(false);

      $select.trigger('change');
      expect(pattern._changed).to.be.equal(true);

      $(this.$el).on('submit', function(e) {
        var returnedString = pattern._handleUnload(pattern, e);
        var returnValue = e.returnValue;
        if (e.returnValue === undefined) {
          // If we are testing in a Safari based browser, e.g. PhantomJS
          // then e.returnValue is not set, it just reads the string for
          // dialog message
          returnValue = returnedString;
        }
        expect(returnValue).to.not.equal(pattern.options.message);
        // Need to prevent action from doing it's default thing otherwise
        // we get stuck in a loop.
        e.preventDefault();
        done();
      });
      $(this.$el).trigger('submit');
    });
    it.skip('shows the right message on beforeunload event', function(done) {
      registry.scan(this.$el);
      var returnValue = '';
      // current instance of the pattern
      var pattern = this.$el.data('pattern-formunloadalert');
      var $select = $('select', this.$el);

      // Override the _handleMsg of the pattern as we need to
      // get the msg string out somehow, and there's no way to
      // do this that I can find after triggering beforeunload

      pattern._handleMsg = function(e, msg) {
        // Set the msg into a variable that we can actually read
        returnValue = msg;
      };

      expect(pattern._changed).to.be.equal(false);
      $select.trigger('change');
      expect(pattern._changed).to.be.equal(true);

      $(window).on('messageset.formunloadalert.patterns', function() {
        expect(returnValue).to.equal(pattern.options.message);
        done();
      });
      // Trigger the beforeunload event
      $(window).trigger('beforeunload');
    });
    it('doesn\'t interfere if there\'s no form', function() {
      this.$el = $('' +
        '<div class="pat-formunloadalert">' +
        ' <select name="aselect">' +
        '    <option value="1">1</option>' +
        '    <option value="2">2</option>' +
        '</select>' +
        '<input id="b1" type="submit" value="Submit" />' +
        '<a href="patterns.html">Click here to go somewhere else</a>' +
        '</div>');
      registry.scan(this.$el);

      var pattern = this.$el.data('pattern-formunloadalert');
      var $select = $('select', this.$el);

      expect(pattern._changed).to.be.equal(false);
      $select.trigger('change');
      // This should make no differnce, as there was no form so
      // the pattern should have exited.
      expect(pattern._changed).to.be.equal(false);
    });
  });

});
