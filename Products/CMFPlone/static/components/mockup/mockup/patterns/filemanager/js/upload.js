define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover',
  'mockup-patterns-upload'
], function($, _, Backbone, PopoverView, Upload) {
  'use strict';

  var UploadView = PopoverView.extend({
    className: 'popover upload',
    title: _.template('<%= _t("Upload") %>'),
    content: _.template(
      '<span>Location: <span class="current-path"></span></span>' +
      '<input type="text" name="upload" style="display:none" />' +
      '<div class="uploadify-me"></div>'),
    render: function() {
      var self = this;
      PopoverView.prototype.render.call(this);
      self.upload = new Upload(self.$('.uploadify-me').addClass('pat-upload'), {
        url: self.app.options.uploadUrl,
        success: function(response) {
          if( self.callback ) {
            if( response.status == "success" ) {  
              self.callback.apply(self.app, [response]);
            }
            else
            {
                alert("There was a problem during the upload process");
            }
          }
        }
      });
      return this;
    },
    toggle: function(button, e) {
      /* we need to be able to change the current default upload directory */
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
      if (!this.opened) {
        return;
      }
    }

  });

  return UploadView;
});
