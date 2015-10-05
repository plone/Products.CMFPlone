var tests = Object.keys(window.__karma__.files).filter(function (file) {
  'use strict';

  var pattern,
      args = window.__karma__.config.args;
  if (args) {
    // workaround for cmd line arguments not parsed
    if (Object.prototype.toString.call(args) === '[object Array]') {
      args.join(' ').replace(/--pattern[\s|=]+(\S+)?\s*/, function(match, value) {
        pattern = value;
      });
    }
    if (pattern) {
      return (new RegExp(pattern + '-test.js$')).test(file);
    }
  }

  return (/\-test\.js$/).test(file);
});

requirejs.config({
  // Karma serves files from '/base'
  baseUrl: '/base',

  // ask Require.js to load these files (all our tests)
  deps: tests,

  // start test run, once Require.js is done
  callback: window.__karma__.start
});

window.DEBUG = true;
