/* RequireJS configuration
 */

/* global module:true */

(function() {
  'use strict';

  var tinymcePlugins = [
    'advlist', 'anchor', 'autolink', 'autoresize', 'autosave', 'bbcode',
    'charmap', 'code', 'colorpicker', 'contextmenu', 'directionality',
    'emoticons', 'fullpage', 'fullscreen', 'hr', 'image', 'importcss',
    'insertdatetime', 'layer', 'legacyoutput', 'link', 'lists', 'media',
    'nonbreaking', 'noneditable', 'pagebreak', 'paste', 'preview', 'print',
    'save', 'searchreplace', 'spellchecker', 'tabfocus', 'table', 'template',
    'textcolor', 'textpattern', 'visualblocks', 'visualchars', 'wordcount',
    'compat3x'
  ];

  var requirejsOptions = {
    baseUrl: './',
    optimize: 'none',
    paths: {
      'JSXTransformer': 'bower_components/react/JSXTransformer',
      'ace': 'bower_components/ace-builds/src/ace',
      'backbone': 'bower_components/backbone/backbone',
      'backbone.paginator': 'bower_components/backbone.paginator/lib/backbone.paginator',
      'bootstrap-alert': 'bower_components/bootstrap/js/alert',
      'bootstrap-collapse': 'bower_components/bootstrap/js/collapse',
      'bootstrap-dropdown': 'bower_components/bootstrap/js/dropdown',
      'bootstrap-transition': 'bower_components/bootstrap/js/transition',
      'docs-contribute': 'CONTRIBUTE.md',
      'docs-getting-started': 'GETTING_STARTED.md',
      'docs-learn': 'LEARN.md',
      'dropzone': 'bower_components/dropzone/dist/dropzone-amd-module',
      'expect': 'bower_components/expect/index',
      'jqtree': 'bower_components/jqtree/tree.jquery',
      'jquery': 'bower_components/jquery/dist/jquery',
      'jquery.cookie': 'bower_components/jquery.cookie/jquery.cookie',
      'jquery.event.drag': 'lib/jquery.event.drag',
      'jquery.event.drop': 'lib/jquery.event.drop',
      'jquery.form': 'bower_components/jquery-form/jquery.form',
      'jquery.recurrenceinput': 'bower_components/jquery.recurrenceinput.js/src/jquery.recurrenceinput',
      'jquery.tools.dateinput': 'bower_components/jquery.recurrenceinput.js/lib/jquery.tools.dateinput',
      'jquery.tools.overlay': 'bower_components/jquery.recurrenceinput.js/lib/jquery.tools.overlay',
      'jquery.tmpl': 'bower_components/jquery.recurrenceinput.js/lib/jquery.tmpl',
      'translate': 'js/i18n-wrapper',
      'marked': 'bower_components/marked/lib/marked',
      'mockup-bundles-docs': 'js/bundles/docs',
      'mockup-bundles-filemanager': 'js/bundles/filemanager',
      'mockup-bundles-plone': 'js/bundles/plone',
      'mockup-bundles-resourceregistry': 'js/bundles/resourceregistry',
      'mockup-bundles-structure': 'js/bundles/structure',
      'mockup-bundles-tiles': 'js/bundles/widgets',
      'mockup-bundles-widgets': 'js/bundles/widgets',
      'mockup-docs': 'bower_components/mockup-core/js/docs/app',
      'mockup-docs-navigation': 'bower_components/mockup-core/js/docs/navigation',
      'mockup-docs-page': 'bower_components/mockup-core/js/docs/page',
      'mockup-docs-pattern': 'bower_components/mockup-core/js/docs/pattern',
      'mockup-docs-view': 'bower_components/mockup-core/js/docs/view',
      'mockup-fakeserver': 'tests/fakeserver',
      'mockup-i18n': 'js/i18n',
      'mockup-parser': 'bower_components/mockup-core/js/parser',
      'mockup-patterns-autotoc': 'patterns/autotoc/pattern',
      'mockup-patterns-backdrop': 'patterns/backdrop/pattern',
      'mockup-patterns-base': 'bower_components/mockup-core/js/pattern',
      'mockup-patterns-contentloader': 'patterns/contentloader/pattern',
      'mockup-patterns-cookietrigger': 'patterns/cookietrigger/pattern',
      'mockup-patterns-eventedit': 'patterns/eventedit/pattern',
      'mockup-patterns-filemanager': 'patterns/filemanager/pattern',
      'mockup-patterns-filemanager-url': 'patterns/filemanager',
      'mockup-patterns-formautofocus': 'patterns/formautofocus/pattern',
      'mockup-patterns-formunloadalert': 'patterns/formunloadalert/pattern',
      'mockup-patterns-inlinevalidation': 'patterns/inlinevalidation/pattern',
      'mockup-patterns-markspeciallinks': 'patterns/markspeciallinks/pattern',
      'mockup-patterns-modal': 'patterns/modal/pattern',
      'mockup-patterns-moment': 'patterns/moment/pattern',
      'mockup-patterns-pickadate': 'patterns/pickadate/pattern',
      'mockup-patterns-preventdoublesubmit': 'patterns/preventdoublesubmit/pattern',
      'mockup-patterns-querystring': 'patterns/querystring/pattern',
      'mockup-patterns-relateditems': 'patterns/relateditems/pattern',
      'mockup-patterns-recurrence': 'patterns/recurrence/pattern',
      'mockup-patterns-resourceregistry': 'patterns/resourceregistry/pattern',
      'mockup-patterns-resourceregistry-url': 'patterns/resourceregistry',
      'mockup-patterns-select2': 'patterns/select2/pattern',
      'mockup-patterns-sortable': 'patterns/sortable/pattern',
      'mockup-patterns-structure': 'patterns/structure/pattern',
      'mockup-patterns-structure-url': 'patterns/structure',
      'mockup-patterns-textareamimetypeselector': 'patterns/textareamimetypeselector/pattern',
      'mockup-patterns-texteditor': 'patterns/texteditor/pattern',
      'mockup-patterns-thememapper': 'patterns/thememapper/pattern',
      'mockup-patterns-thememapper-url': 'patterns/thememapper',
      'mockup-patterns-tinymce': 'patterns/tinymce/pattern',
      'mockup-patterns-tinymce-url': 'patterns/tinymce',
      'mockup-patterns-toggle': 'patterns/toggle/pattern',
      'mockup-patterns-tooltip': 'patterns/tooltip/pattern',
      'mockup-patterns-tree': 'patterns/tree/pattern',
      'mockup-patterns-upload': 'patterns/upload/pattern',
      'mockup-patterns-upload-url': 'patterns/upload',
      'mockup-patterns-passwordstrength': 'patterns/passwordstrength/pattern',
      'mockup-patterns-passwordstrength-url': 'patterns/passwordstrength',
      'mockup-patterns-livesearch': 'patterns/livesearch/pattern',
      'mockup-router': 'js/router',
      'mockup-ui-url': 'js/ui',
      'mockup-utils': 'js/utils',
      'moment': 'bower_components/moment/moment',
      'picker': 'bower_components/pickadate/lib/picker',
      'picker.date': 'bower_components/pickadate/lib/picker.date',
      'picker.time': 'bower_components/pickadate/lib/picker.time',
      'react': 'bower_components/react/react',
      'select2': 'bower_components/select2/select2',
      'sinon': 'bower_components/sinonjs/sinon',
      'text': 'bower_components/requirejs-text/text',
      'tinymce': 'bower_components/tinymce-builded/js/tinymce/tinymce',
      'tinymce-modern-theme': 'bower_components/tinymce-builded/js/tinymce/themes/modern/theme',
      'underscore': 'bower_components/lodash/dist/lodash.underscore',

      // Patternslib
      'pat-compat': 'bower_components/patternslib/src/core/compat',
      'pat-jquery-ext': 'bower_components/patternslib/src/core/jquery-ext',
      'pat-logger': 'bower_components/patternslib/src/core/logger',
      'pat-registry': 'bower_components/patternslib/src/core/registry',
      'pat-utils': 'bower_components/patternslib/src/core/utils',
      'logging': 'bower_components/logging/src/logging'
    },
    shim: {
      'JSXTransformer': { exports: 'window.JSXTransformer' },
      'backbone': { exports: 'window.Backbone', deps: ['underscore', 'jquery'] },
      'backbone.paginator': { exports: 'window.Backbone.Paginator', deps: ['backbone'] },
      'bootstrap-alert': {  exports: 'window.jQuery.fn.alert.Constructor', deps: ['jquery'] },
      'bootstrap-collapse': { exports: 'window.jQuery.fn.collapse.Constructor', deps: ['jquery'] },
      'bootstrap-dropdown': { exports: 'window.jQuery.fn.dropdown.Constructor', deps: ['jquery'] },
      'bootstrap-transition': { exports: 'window.jQuery.support.transition', deps: ['jquery'] },
      'expect': { exports: 'window.expect' },
      'jqtree': { deps: ['jquery'] },
      'jquery.cookie': { deps: ['jquery'] },
      'jquery.event.drag': { deps: ['jquery'] },
      'jquery.event.drop': { deps: ['jquery'], exports: '$.drop' },
      'picker.date': { deps: [ 'picker' ] },
      'picker.time': { deps: [ 'picker' ] },
      'sinon': { exports: 'window.sinon' },
      'tinymce': {
        exports: 'window.tinyMCE',
        init: function () {
          this.tinyMCE.DOM.events.domLoaded = true;
          return this.tinyMCE;
        },
      },
      'tinymce-modern-theme': { deps: ['tinymce'] },
      'underscore': { exports: 'window._' },
      'jquery.recurrenceinput': {
        deps: [
          'jquery',
          'jquery.tools.overlay',
          'jquery.tools.dateinput',
          'jquery.tmpl'
        ]
      },
      'jquery.tools.dateinput': { deps: ['jquery'] },
      'jquery.tools.overlay': { deps: ['jquery'] },
      'jquery.tmpl': { deps: ['jquery'] }
    },
    wrapShim: true
  };
  for(var i=0; i<tinymcePlugins.length; i=i+1){
    var plugin = tinymcePlugins[i];
    requirejsOptions.paths['tinymce-' + plugin] = 'bower_components/tinymce-builded/js/tinymce/plugins/' + plugin + '/plugin';
    requirejsOptions.shim['tinymce-' + plugin] = {
      deps: ['tinymce']
    };
  }

  if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
    module.exports = requirejsOptions;
  }
  if (typeof requirejs !== 'undefined' && requirejs.config) {
    requirejs.config(requirejsOptions);
  }

}());
