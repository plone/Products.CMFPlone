define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/popover',
  'mockup-patterns-sortable'
], function($, _, Backbone, PopoverView, Sortable) {
  'use strict';

  var ColumnsView = PopoverView.extend({
    className: 'popover attribute-columns',
    title: _.template('<%- _t("Columns") %>'),
    content: _.template(
      '<label><%- _t("Select columns to show, drag and drop to reorder") %></label>' +
      '<ul>' +
      '</ul>' +
      '<button class="btn btn-block btn-success"><%- _t("Save") %></button>'
    ),
    itemTemplate: _.template(
      '<li>' +
        '<label>' +
          '<input type="checkbox" value="<%- id %>"/>' +
          '<%- title %>' +
        '</label>' +
      '</li>'
    ),
    events: {
      'click button': 'applyButtonClicked'
    },
    initialize: function(options) {
      this.app = options.app;
      PopoverView.prototype.initialize.apply(this, [options]);
    },
    afterRender: function() {
      var self = this;

      self.$container = self.$('ul');
      _.each(self.app.activeColumns, function(id) {
        var $el = $(self.itemTemplate({
          title: self.app.availableColumns[id],
          id: id
        }));
        $el.find('input')[0].checked = true;
        self.$container.append($el);
      });
      _.each(_.omit(self.app.availableColumns, self.app.activeColumns), function(name, id) {
        var $el = $(self.itemTemplate({
          title: name,
          id: id
        }));
        self.$container.append($el);
      });

      var dd = new Sortable(self.$container, {
        selector: 'li'
      });
      return this;
    },
    applyButtonClicked: function() {
      var self = this;
      this.hide();
      self.app.activeColumns = [];
      self.$('input:checked').each(function() {
        self.app.activeColumns.push($(this).val());
      });
      self.app.setCookieSetting('activeColumns', this.app.activeColumns);
      self.app.tableView.render();
    }
  });

  return ColumnsView;
});
