define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-patterns-filemanager-url/js/basepopover'
], function($, _, Backbone, PopoverView) {
  'use strict';

  var AddNewView = PopoverView.extend({
    className: 'popover addnew',
    title: _.template('<%= _t("Add new file") %>'),
    content: _.template(
      '<span class="current-path"></span>' +
      '<div class="form-group">' +
        '<label for="filename-field"><%= _t("Filename") %></label>' +
        '<input type="text" class="form-control" ' +
                'id="filename-field" placeholder="<%= _t("Enter filename") %>">' +
      '</div>' +
      '<button class="btn btn-block btn-primary"><%= _t("Add") %></button>'
    ),
    events: {
      'click button': 'addButtonClicked'
    },
    addButtonClicked: function(e) {
      var self = this;
      var $input = self.$('input');
      var filename = $input.val();
      if (filename){
        self.app.doAction('addFile', {
          type: 'POST',
          data: {
            filename: filename,
            path: self.app.getFolderPath()
          },
          success: function(data) {
            self.hide();
            self.data = data;
            self.app.refreshTree(function() {
              var path = self.data.parent + '/' +  self.data.name;
              self.app.selectItem(path);
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
