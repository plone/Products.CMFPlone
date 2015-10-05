define([
  'underscore',
  'backbone',
  'mockup-ui-url/views/container'
], function(_, Backbone, ContainerView) {
  'use strict';

  var Toolbar = ContainerView.extend({
    tagName: 'div',
    className: 'navbar',
    idPrefix: 'toolbar-'
  });

  return Toolbar;
});
