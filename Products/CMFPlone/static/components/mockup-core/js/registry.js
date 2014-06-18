define([
  'jquery'
], function($, undefined) {
  'use strict';

  var Registry = {

    patterns: {},

    warn: function(msg) {
      /* istanbul ignore next */
      if (window.DEBUG && window.console) {
        console.warn(msg);
      }
    },

    getOptions: function($el, patternName, options) {
      options = options || {};

      // get options from parent element first, stop if element tag name is 'body'
      if ($el.length !== 0 && !$.nodeName($el[0], 'body')) {
        options = Registry.getOptions($el.parent(), patternName, options);
      }

      // collect all options from element
      var elOptions = {};
      if ($el.length !== 0) {
        elOptions = $el.data('pat-' + patternName);
        if (elOptions) {
          // parse options if string
          if (typeof(elOptions) === 'string') {
            var tmpOptions = {};
            $.each(elOptions.split(';'), function(i, item) {
              item = item.split(':');
              item.reverse();
              var key = item.pop();
              key = key.replace(/^\s+|\s+$/g, '');  // trim
              item.reverse();
              var value = item.join(':');
              value = value.replace(/^\s+|\s+$/g, '');  // trim
              tmpOptions[key] = value;
            });
            elOptions = tmpOptions;
          }
        }
      }

      return $.extend(true, {}, options, elOptions);
    },

    init: function($el, patternName, options) {
      var pattern = $el.data('pattern-' + patternName);
      if (pattern === undefined && Registry.patterns[patternName]) {
        if (window.DEBUG) {
          pattern = new Registry.patterns[patternName]($el,
              Registry.getOptions($el, patternName, options));
        } else {
          try {
            pattern = new Registry.patterns[patternName]($el,
                Registry.getOptions($el, patternName, options));
          } catch (e) {
            Registry.warn('Failed while initializing "' + patternName + '" pattern.');
          }
        }
        $el.data('pattern-' + patternName, pattern);
      }
      return pattern;
    },

    scan: function(content) {
      var $content = $(content),
          patterns = [];

      patterns = $.merge(patterns, $content.filter('[class*="pat-"]'));
      patterns = $.merge(patterns, $('[class*="pat-"]', $content));

      $.each(patterns, function(i, $el) {
        $el = $($el);
        $.each($el.attr('class').split(' '), function(j, className) {
          if (className.indexOf('pat-') === 0) {
            Registry.init($el, className.substr(4));
          }
        });
      });
    },

    register: function(Pattern) {

      // require name
      if (!Pattern.prototype.name) {
        Registry.warn('Pattern didn\'t specified a name.');
        return false;
      }

      // automatically create jquery plugin from pattern
      if (Pattern.prototype.jqueryPlugin === undefined) {
        Pattern.prototype.jqueryPlugin = 'pattern' +
            Pattern.prototype.name.charAt(0).toUpperCase() +
            Pattern.prototype.name.slice(1);
      }

      $.fn[Pattern.prototype.jqueryPlugin] = function(method, options) {
        $(this).each(function() {
          if (typeof method === 'object') {
            options = method;
            method = undefined;
          }
          var $el = $(this),
              pattern = Registry.init($el, Pattern.prototype.name, options);

          if (method) {
            if (pattern[method] === undefined) {
              Registry.warn('Method "' + method + '" does not exists.');
              return false;
            }
            if (method.charAt(0) === '_') {
              Registry.warn('Method "' + method + '" is private.');
              return false;
            }
            pattern[method].apply(pattern, [options]);
          }
        });
        return this;
      };

      Registry.patterns[Pattern.prototype.name] = Pattern;
    }

  };

  return Registry;
});
