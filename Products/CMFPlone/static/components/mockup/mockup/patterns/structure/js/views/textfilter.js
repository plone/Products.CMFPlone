define([
  'jquery',
  'backbone',
  'underscore',
  'mockup-ui-url/views/base',
  'mockup-ui-url/views/button',
  'mockup-ui-url/views/popover',
  'mockup-patterns-querystring',
  'translate'
], function($, Backbone, _, BaseView, ButtonView, PopoverView, QueryString, _t) {
  'use strict';

  var TextFilterView = BaseView.extend({
    tagName: 'div',
    className: 'navbar-search form-search ui-offset-parent',
    template: _.template(
      '<div class="input-group">' +
      '<input type="text" class="form-control search-query" placeholder="<%- _t("Filter") %>">' +
      '<span class="input-group-btn">' +
      '</span>' +
      '</div>'
    ),
    popoverContent: _.template(
      '<input class="pat-querystring" />'
    ),
    events: {
      'keyup .search-query': 'filter'
    },
    term: null,
    timeoutId: null,
    keyupDelay: 300,

    initialize: function(options) {
      BaseView.prototype.initialize.apply(this, [options]);
      this.app = this.options.app;
    },

    render: function() {
      this.$el.html(this.template({_t: _t}));
      this.button = new ButtonView({
        title: _t('Query'),
        icon: 'search'
      });
      this.popover = new PopoverView({
        triggerView: this.button,
        title: _.template(_t('Query')),
        content: this.popoverContent,
        placement: 'left'
      });
      this.$('.input-group-btn').append(this.button.render().el);
      this.$el.append(this.popover.render().el);
      this.popover.$el.addClass('query');
      this.$queryString = this.popover.$('input.pat-querystring');
      this.queryString = new QueryString(
        this.$queryString, {
          indexOptionsUrl: this.app.options.indexOptionsUrl,
          showPreviews: false
        });
      var self = this;
      self.queryString.$el.on('change', function() {
        if (self.timeoutId) {
          clearTimeout(self.timeoutId);
        }
        self.timeoutId = setTimeout(function() {
          var criterias = $.parseJSON(self.$queryString.val());
          self.app.additionalCriterias = criterias;
          self.app.collection.pager();
        }, this.keyupDelay);
      });
      self.queryString.$el.on('initialized', function() {
        self.queryString.$sortOn.on('change', function() {
          self.app['sort_on'] = self.queryString.$sortOn.val(); // jshint ignore:line
          self.app.collection.pager();
        });
        self.queryString.$sortOrder.change(function() {
          if (self.queryString.$sortOrder[0].checked) {
            self.app['sort_order'] = 'reverse'; // jshint ignore:line
          } else {
            self.app['sort_order'] = 'ascending'; // jshint ignore:line
          }
          self.app.collection.pager();
        });
      });
      return this;
    },

    filter: function(event) {
      var self = this;
      if (self.timeoutId) {
        clearTimeout(self.timeoutId);
      }
      self.timeoutId = setTimeout(function() {
        self.term = $(event.currentTarget).val();
        self.app.collection.pager();
      }, this.keyupDelay);
    }
  });

  return TextFilterView;
});
