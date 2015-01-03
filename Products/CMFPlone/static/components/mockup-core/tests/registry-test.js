// Tests for Registry

define([
  'expect',
  'sinon',
  'jquery',
  'mockup-registry'
], function(expect, sinon, $, Registry) {
  'use strict';

  window.mocha.setup('bdd');

  describe('Registry', function () {
    beforeEach(function() {
      var self = this;
      self.warnMsg = '';
      self._warn = Registry.warn;
      Registry.warn = function(msg) {
        self.warnMsg = msg;
      };
      Registry.error = function(msg) {
        self.warnMsg = msg;
      };
      self.jqueryPatterns = {};
      $.each(Registry.patterns, function(patternName) {
        self.jqueryPatterns[Registry.patterns[patternName].prototype.jqueryPlugin] = $.fn[Registry.patterns[patternName].prototype.jqueryPlugin];
        $.fn[Registry.patterns[patternName].prototype.jqueryPlugin] = undefined;
      });
      self._patterns = Registry.patterns;
      Registry.patterns = {};
    });
    afterEach(function() {
      var self = this, jqueryPlugin;
      self.warnMsg = '';
      Registry.warn = self._warn;
      $.each(Registry.patterns, function(patternName) {
        $.fn[Registry.patterns[patternName].prototype.jqueryPlugin] = undefined;
      });
      Registry.patterns = self._patterns;
      $.each(Registry.patterns, function(patternName) {
        jqueryPlugin = Registry.patterns[patternName].prototype.jqueryPlugin;
        $.fn[jqueryPlugin] = self.jqueryPatterns[jqueryPlugin];
      });
    });

    it('skip initializing pattern if not in registry', function() {
      var $el = $('<div/>');
      Registry.init($el, 'example', {});
      expect($el.data('example')).to.be.equal(undefined);
    });

    it('failing pattern initialization', function() {
      window.DEBUG = false;
      Registry.patterns.example = function($el, options) {
        throw new Error('some random error');
      };
      Registry.init($('<div/>'), 'example', {});
      expect(this.warnMsg).to.be.equal('Failed while initializing "example" pattern.');
      window.DEBUG = true;
    });

    it('pattern initialization', function() {
      var $pattern = $('<div/>');
      Registry.patterns.example = function($el, options) {
        this.example = 'works';
      };
      Registry.init($pattern, 'example', {});
      expect($pattern.data('pattern-example').example).to.be.equal('works');
    });

    it('pattern wont get initialized twice', function() {
      var $pattern = $('<div/>');
      Registry.patterns.example = function($pattern, options) {
        this.example = 'works';
      };
      var pattern1 = Registry.init($pattern, 'example', {});
      pattern1.example2 = 'works';
      var pattern2 = Registry.init($pattern, 'example', {});
      expect(pattern1).to.be.equal(pattern2);
      expect(pattern2.example2).to.be.equal('works');
      expect(pattern1.example2).to.be.equal('works');
    });

    it('scan for pattern', function() {
      var $dom = $('' +
        '<div class="pat-example">' +
        '  <div class="pat-example" />' +
        '</div>');
      Registry.patterns.example = function($el, options) {
        this.example = 'works';
      };
      Registry.scan($dom);
      expect($dom.data('pattern-example').example).to.be.equal('works');
      expect($dom.find('div').data('pattern-example').example).to.be.equal('works');
    });

    it('scan for pattern among other class names on element', function() {
      var $el = $('<div class="some-other-stuff pat-example" />');
      Registry.patterns.example = function($el, options) {
        this.example = 'works';
      };
      Registry.scan($el);
      expect($el.data('pattern-example').example).to.be.equal('works');
    });

    it('trigger event on completed scan', function () {
      var spy = sinon.spy();
      // register spy as event listener
      $(document).on('scan-completed.registry.mockup-core', spy);
      var $el = $('<div />');
      Registry.scan($el);
      expect(spy.called).to.be(true);  // spy must be called
    });

    it('try register a pattern without name', function() {
      Registry.register(function($el, options) {});
      expect(this.warnMsg).to.be.equal('Pattern didn\'t specified a name.');
    });

    it('register a pattern', function() {
      var ExamplePattern = function($el, options) { };
      ExamplePattern.prototype.name = 'example';
      Registry.register(ExamplePattern);
      expect(Registry.patterns.example).to.be.equal(ExamplePattern);
      expect($.fn.patternExample).to.not.equal(undefined);
    });

    it('custom jquery plugin name for pattern', function() {
      var ExamplePattern = function($el, options) { };
      ExamplePattern.prototype.name = 'example';
      ExamplePattern.prototype.jqueryPlugin = 'example';
      Registry.register(ExamplePattern);
      expect($.fn.patternExample).to.be.equal(undefined);
      expect($.fn.example).to.not.equal(undefined);
    });

    it('jquery plugin with custom options', function() {
      var ExamplePattern = function($el, options) {
        this.options = options;
      };
      ExamplePattern.prototype.name = 'example';

      Registry.register(ExamplePattern);

      var self = this,
          $el = $('<div/>');

      $el.patternExample({option1: 'value1'});

      expect($el.data('pattern-example').options.option1).to.be.equal('value1');
    });

    it('call methods via jquery plugin', function() {
      var ExamplePattern = function($el, options) { }, value = '';
      ExamplePattern.prototype.name = 'example';
      ExamplePattern.prototype.method = function() { value = 'method'; };
      ExamplePattern.prototype.methodWithOptions = function(options) {
        if (options.optionA && options.optionA === 'valueA') {
          value = 'methodWithOptions';
        }
      };
      ExamplePattern.prototype._methodPrivate = function() { };
      Registry.register(ExamplePattern);

      var self = this, $el = $('<div/>');

      value = '';
      $el.patternExample('method_non_existing');
      expect(value).to.be.equal('');
      expect(self.warnMsg).to.be.equal('Method "method_non_existing" does not exists.');

      value = '';
      $el.patternExample('method');
      expect(value).to.be.equal('method');

      value = '';
      $el.patternExample('methodWithOptions', {optionA: 'valueB'});
      expect(value).to.be.equal('');

      value = '';
      $el.patternExample('methodWithOptions', {optionA: 'valueA'});
      expect(value).to.be.equal('methodWithOptions');

      value = '';
      $el.patternExample('_methodPrivate');
      expect(value).to.be.equal('');
      expect(self.warnMsg).to.be.equal('Method "_methodPrivate" is private.');
    });

    it('read options from dom tree', function() {
      var $el = $('' +
        '<div data-pat-example="{&quot;name1&quot;: &quot;value1&quot;,' +
        '    &quot;name2&quot;: &quot;value2&quot;}">' +
        ' <div class="pat-example"' +
        '      data-pat-example="name2: something;' +
        '                        some-thing-name4: value4;' +
        '                        some-stuff: value5"/>' +
        '</div>');

      var options = Registry.getOptions(
        $('.pat-example', $el),
        'example',
        { name3: 'value3'}
      );

      expect(options.name1).to.equal('value1');
      expect(options.name2).to.equal('something');
      expect(options.name3).to.equal('value3');
      expect(options['some-thing-name4']).to.equal('value4');
      expect(options['some-stuff']).to.equal('value5');
    });

  });

});
