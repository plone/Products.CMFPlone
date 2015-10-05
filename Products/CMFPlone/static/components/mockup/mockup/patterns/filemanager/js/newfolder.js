define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover'
], function($, _, Backbone, PopoverView) {
  'use strict';

  var AddNewView = PopoverView.extend({
    className: 'popover addfolder',
    title: _.template('<%= _t("New folder") %>'),
    content: _.template(
      '<span class="current-path"></span>' +
      '<div class="form-group">' +
        '<label for="filename-field"><%= _t("Add new folder to current directory") %></label>' +
        '<input type="email" class="form-control" ' +
                'id="filename-field" placeholder="<%= _t("Enter folder name") %>">' +
      '</div>' +
      '<button class="btn btn-block btn-primary"><%= _t("Add") %></button>'
    ),
    events: {
      'click button': 'addButtonClicked'
    },
    addButtonClicked: function(e) {
      var self = this;
      var $input = self.$('input');
      var name = $input.val();
      if (name){
        self.app.doAction('addFolder', {
          type: 'POST',
          data: {
            name: name,
            path: self.app.getFolderPath()
          },
          success: function(data) {
            self.hide();
            self.data = data;
            self.app.refreshTree(function() {
              var node = self.app.getNodeByPath(self.data.parent);
              self.app.$tree.tree('openNode', node);
              delete self.data;
            });
          }
        });
        // XXX show loading
      } else {
        self.$('.form-group').addClass('has-error');
      }
    }
  });

  return AddNewView;
});
