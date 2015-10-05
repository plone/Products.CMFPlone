define([
  'jquery'
], function($) {
  'use strict';

  var parser = {
    getOptions: function getOptions($el, patternName, options) {
      /* This is the Mockup parser. It parses a DOM element for pattern
      * configuration options.
      */
      options = options || {};
      // get options from parent element first, stop if element tag name is 'body'
      if ($el.length !== 0 && !$.nodeName($el[0], 'body')) {
        options = getOptions($el.parent(), patternName, options);
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
    }
  };
  return parser;
});
