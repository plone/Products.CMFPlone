/*jshint ignore:start */

// From https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter
if (!Array.prototype.filter) {
  Array.prototype.filter = function(fun /*, thisp */)
  {
    'use strict';

    if (this === null)
      throw new TypeError();

    var t = Object(this);
    var len = t.length >>> 0;
    if (typeof fun != 'function')
      throw new TypeError();

    var res = [];
    var thisp = arguments[1];
    for (var i = 0; i < len; i++)
    {
      if (i in t)
      {
        var val = t[i]; // in case fun mutates this
        if (fun.call(thisp, val, i, t))
          res.push(val);
      }
    }

    return res;
  };
}

// From https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/keys
if (!Object.keys) {
  Object.keys = (function () {
    'use strict';
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length;

    return function (obj) {
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
        throw new TypeError('Object.keys called on non-object');
      }

      var result = [], prop, i;

      for (prop in obj) {
        if (hasOwnProperty.call(obj, prop)) {
          result.push(prop);
        }
      }

      if (hasDontEnumBug) {
        for (i = 0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) {
            result.push(dontEnums[i]);
          }
        }
      }
      return result;
    };
  }());
}

// https://github.com/facebook/react/blob/master/src/test/phantomjs-shims.js
(function() {

  var Ap = Array.prototype;
  var slice = Ap.slice;
  var Fp = Function.prototype;

  if (!Fp.bind) {
    // PhantomJS doesn't support Function.prototype.bind natively, so
    // polyfill it whenever this module is required.
    Fp.bind = function(context) {
      var func = this;
      var args = slice.call(arguments, 1);

      function bound() {
        var invokedAsConstructor = func.prototype && (this instanceof func);
        return func.apply(
          // Ignore the context parameter when invoking the bound function
          // as a constructor. Note that this includes not only constructor
          // invocations using the new keyword but also calls to base class
          // constructors such as BaseClass.call(this, ...) or super(...).
          !invokedAsConstructor && context || this,
          args.concat(slice.call(arguments))
        );
      }

      // The bound function must share the .prototype of the unbound
      // function so that any object created by one constructor will count
      // as an instance of both constructors.
      bound.prototype = func.prototype;

      return bound;
    };
  }

})();

/*jshint ignore:end*/


var tests = Object.keys(window.__karma__.files).filter(function (file) {
  'use strict';

  if (window.__karma__.config.args.pattern) {
    return (new RegExp(window.__karma__.config.args.pattern + '-test.js$')).test(file);
  }
  return (/\-test\.js$/).test(file);

});

requirejs.config({
  baseUrl: '/base',
  deps: tests,
  callback: window.__karma__.start
});

window.DEBUG = true;
