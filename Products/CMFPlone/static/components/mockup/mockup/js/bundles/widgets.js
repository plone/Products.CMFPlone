define([
  'jquery',
  'pat-registry',
  'mockup-patterns-base',

  'mockup-patterns-select2',
  'mockup-patterns-passwordstrength',
  'mockup-patterns-pickadate',
  'mockup-patterns-recurrence',
  'mockup-patterns-relateditems',
  'mockup-patterns-querystring',
  'mockup-patterns-textareamimetypeselector',
  'mockup-patterns-tinymce'
], function($, registry, Base) {
  'use strict';

  var PloneWidgets = Base.extend({
    name: 'plone-widgets',
    init: function() {
      var self = this;
    }
  });

  // initialize only if we are in top frame
  if (window.parent === window) {
    $(document).ready(function() {
      $('body').addClass('pat-plone-widgets');
      if (!registry.initialized) {
        registry.init();
      }
    });
  }
  return PloneWidgets;
});
