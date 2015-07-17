/* Base Pattern
 */

define([
  'jquery',
  'pat-registry',
  'mockup-parser',
  "pat-logger"
], function($, Registry, mockupParser, logger) {
  'use strict';
  var log = logger.getLogger("Mockup Base");

  var initMockup = function initMockup($el, options, trigger) {
    var name = this.prototype.name;
    var log = logger.getLogger("pat." + name);
    var pattern = $el.data('pattern-' + name);
    if (pattern === undefined && Registry.patterns[name]) {
      options = this.prototype.parser === "mockup" ? mockupParser.getOptions($el, name, options) : options;
      try {
          pattern = new Registry.patterns[name]($el, options);
      } catch (e) {
          log.error('Failed while initializing "' + name + '" pattern.', e);
      }
      $el.data('pattern-' + name, pattern);
    }
    return pattern;
  };

  // Base Pattern
  var Base = function($el, options) {
    this.$el = $el;
    this.options = $.extend(true, {}, this.defaults || {}, options || {});
    this.init($el, options);
    this.emit('init');
  };

  Base.prototype = {
    constructor: Base,
    on: function(eventName, eventCallback) {
      this.$el.on(eventName + '.' + this.name + '.patterns', eventCallback);
    },
    emit: function(eventName, args) {
      // args should be a list
      if (args === undefined) {
        args = [];
      }
      this.$el.trigger(eventName + '.' + this.name + '.patterns', args);
    }
  };

  Base.extend = function(patternProps) {
    /* Helper function to correctly set up the prototype chain for new patterns.
     */
    var parent = this;
    var child;

    // Check that the required configuration properties are given.
    if (!patternProps) {
      throw new Error("Pattern configuration properties required when calling Base.extend");
    }

    // The constructor function for the new subclass is either defined by you
    // (the "constructor" property in your `extend` definition), or defaulted
    // by us to simply call the parent's constructor.
    if (patternProps.hasOwnProperty('constructor')) {
      child = patternProps.constructor;
    } else {
      child = function() { parent.apply(this, arguments); };
    }

    // Allow patterns to be extended indefinitely
    child.extend = Base.extend;

    // Static properties required by the Patternslib registry 
    child.init = initMockup;
    child.jquery_plugin = true;
    child.trigger = patternProps.trigger;

    // Set the prototype chain to inherit from `parent`, without calling
    // `parent`'s constructor function.
    var Surrogate = function() { this.constructor = child; };
    Surrogate.prototype = parent.prototype;
    child.prototype = new Surrogate();

    // Fall back to mockup parser if not specified otherwise.
    patternProps.parser = patternProps.parser || 'mockup';

    // Add pattern's configuration properties (instance properties) to the subclass,
    $.extend(true, child.prototype, patternProps);

    // Set a convenience property in case the parent's prototype is needed
    // later.
    child.__super__ = parent.prototype;

    // Register the pattern in the Patternslib registry.
    if (!patternProps.name) {
      log.warn("This mockup pattern without a name attribute will not be registered!");
    } else if (!patternProps.trigger) {
      log.warn("The mockup pattern '"+patternProps.name+"' does not have a trigger attribute, it will not be registered.");
    } else {
      Registry.register(child, patternProps.name);
    }
    return child;
  };
  return Base;
});
