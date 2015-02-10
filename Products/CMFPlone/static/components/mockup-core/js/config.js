/* RequireJS configuration
 */

/* global module:true */

(function() {
  'use strict';

  var requirejsOptions = {
    baseUrl: './',
    optimize: 'uglify',
    paths: {
      'JSXTransformer': 'bower_components/react/JSXTransformer',
      'backbone': 'bower_components/backbone/backbone',
      'bootstrap-collapse': 'bower_components/bootstrap/js/collapse',
      'bootstrap-transition': 'bower_components/bootstrap/js/transition',
      'expect': 'bower_components/expect/index',
      'jquery': 'bower_components/jquery/dist/jquery',
      'marked': 'bower_components/marked/lib/marked',
      'mockup-docs': 'js/docs/app',
      'mockup-docs-navigation': 'js/docs/navigation',
      'mockup-docs-page': 'js/docs/page',
      'mockup-docs-pattern': 'js/docs/pattern',
      'mockup-docs-view': 'js/docs/view',
      'mockup-parser': 'js/parser',
      'mockup-registry': 'js/registry',
      'mockup-patterns-base': 'js/pattern',
      'react': 'bower_components/react/react',
      'sinon': 'bower_components/sinonjs/sinon',
      'text': 'bower_components/requirejs-text/text',
      'underscore': 'bower_components/lodash/dist/lodash.underscore',

      // Patternslib
      'pat-compat': 'bower_components/patternslib/src/core/compat',
      'pat-jquery-ext': 'bower_components/patternslib/src/core/jquery-ext',
      'pat-logger': 'bower_components/patternslib/src/core/logger',
      'pat-parser': 'bower_components/patternslib/src/core/parser',
      'pat-utils': 'bower_components/patternslib/src/core/utils',
      'logging': 'bower_components/logging/src/logging'
    },
    shim: {
      'backbone': {exports: 'window.Backbone', deps: ['underscore', 'jquery']},
      'bootstrap-collapse': {exports: 'window.jQuery.fn.collapse.Constructor', deps: ['jquery']},
      'bootstrap-transition': {exports: 'window.jQuery.support.transition', deps: ['jquery']},
      'expect': {exports: 'window.expect'},
      'sinon': {exports: 'window.sinon'},
      'underscore': {exports: 'window._'}
    }
  };

  /* istanbul ignore next */
  if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
    module.exports = requirejsOptions;
  }
  /* istanbul ignore next */
  if (typeof requirejs !== 'undefined' && requirejs.config) {
    requirejs.config(requirejsOptions);
  }

}());
