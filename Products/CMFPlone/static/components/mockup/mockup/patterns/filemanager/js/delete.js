define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover'
], function($, _, Backbone, PopoverView) {
  'use strict';

  var DeleteView = PopoverView.extend({
    className: 'popover delete',
    title: _.template('<%= _t("Delete") %>'),
    content: _.template(
      '<span class="current-path"></span>' +
      '<p><%= _t("Are you sure you want to delete this resource?") %></p>' +
      '<button class="btn btn-block btn-danger"><%= _t("Yes, delete") %></button>'
    ),
    events: {
      'click button': 'deleteButtonClicked'
    },
    getPath: function() {
      return this.app.getNodePath();
    },
    deleteButtonClicked: function(e) {
      var self = this;
      var path = self.app.getNodePath();
      if( path === undefined ) {
        alert("No file selected.");
        return;
      }
      self.app.doAction('delete', {
        type: 'POST',
        data: {
          path: path
        },
        success: function(data) {
          self.hide();
          self.data = data;
          self.app.refreshTree(function() {

            var parent = self.data.path;
            parent = parent.substr(0, parent.lastIndexOf('/'));

            var node = self.app.getNodeByPath(parent);
            if( node !== null ) {
                self.app.$tree.tree('openNode', node);
            }

            self.app.closeActiveTab();

            delete self.app.fileData[self.data.path];
            delete self.data;
          });
          self.app.resizeEditor();
        }
      });
      // XXX show loading
    }
  });

  return DeleteView;
});
