define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/popover'
], function($, _, Backbone, PopoverView) {
  'use strict';

  var FileManagerPopover = PopoverView.extend({
    className: 'popover',
    title: _.template('nothing'),
    content: _.template('<div/>'),
    initialize: function(options) {
      this.app = options.app;
      PopoverView.prototype.initialize.apply(this, [options]);
    },
    render: function() {
      var self = this;
      PopoverView.prototype.render.call(this);
      return self;
    },
    toggle: function(button, e) {
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
      if (!self.opened) {
        return;
      }
      var $path = self.$('.current-path');
      if ($path.length !== 0){
        $path.html(self.getPath());
      }
    },
    getPath: function() {
      return this.app.getFolderPath();
    }
  });

  return FileManagerPopover;
});
