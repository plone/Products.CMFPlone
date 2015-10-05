define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover',
  'mockup-utils'
], function($, _, Backbone, PopoverView, utils ) {
  'use strict';
  var template = _.template(
    '<div>' +
      '<span id="clearMessage">Click to clear the site\'s theme cache, forcing a reload from the source.</span>' +
      '<span style="display: none;" id="clearSuccess">Cache cleared successfully.</span>' +
      '<a href="#" id="clearBtn" class="btn btn-block btn-primary">Clear</a>' +
    '</div>'
  );

  var CacheView = PopoverView.extend({
    className: 'popover',
    title: _.template('<%= _t("Clear Cache") %>'),
    content: template,
    render: function() {
      var self = this;
      PopoverView.prototype.render.call(this);
      self.$clear = $('#clearBtn', this.$el);
      self.$message = $('#clearMessage', this.$el);
      self.$success = $('#clearSuccess', this.$el);

      self.$clear.on('click', function() {

        var url = self.app.options.themeUrl;
        url = url.substr(0, url.indexOf('portal_resource'));
        url += "/theming-controlpanel";

        $.ajax({
          url: url,
          data: {
            'form.button.InvalidateCache': true,
            '_authenticator': utils.getAuthenticator()
          },
          success: function(response) {
            self.$message.hide();
            self.$success.show();
            self.$clear.hide();

            setTimeout(function() {
              self.$message.show();
              self.$success.hide();
              self.$clear.show();
              self.triggerView.el.click();
            }, 3000);
          }
        });
      });
      return this;
    },
    toggle: function(button, e) {
      PopoverView.prototype.toggle.apply(this, [button, e]);
      var self = this;
    }

  });

  return CacheView;
});
