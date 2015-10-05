define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/popover',
  'mockup-patterns-upload'
], function($, _, Backbone, PopoverView, Upload) {
  'use strict';

  var UploadView = PopoverView.extend({
    className: 'popover upload',
    title: _.template('<%- _t("Upload files") %>'),
    content: _.template(
      '<input type="text" name="upload" style="display:none" />' +
      '<div class="uploadify-me"></div>'),

    initialize: function(options) {
      var self = this;
      self.app = options.app;
      PopoverView.prototype.initialize.apply(self, [options]);
      self.currentPathData = null;
      self.app.on('context-info-loaded', function(data) {
        self.currentPathData = data;
      });
    },

    render: function() {
      var self = this;
      PopoverView.prototype.render.call(this);
      var options = self.app.options.upload;
      options.success = function() {
        self.app.collection.pager();
      };
      options.relatedItems = {
        vocabularyUrl: self.app.options.vocabularyUrl
      };
      options.currentPath = self.app.options.queryHelper.getCurrentPath();
      self.upload = new Upload(self.$('.uploadify-me').addClass('pat-upload'), options);
      return this;
    },

    toggle: function(button, e) {
      /* we need to be able to change the current default upload directory */
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
      if (!this.opened) {
        return;
      }
      var currentPath = self.app.queryHelper.getCurrentPath();
      var relatedItems = self.upload.relatedItems;
      if (self.currentPathData && relatedItems && currentPath !== self.upload.currentPath){
        if (currentPath === '/'){
          relatedItems.$el.select2('data', []);
        } else {
          relatedItems.$el.select2('data', [self.currentPathData.object]);
        }
        self.upload.setPath(currentPath);
      }
    }

  });

  return UploadView;
});





