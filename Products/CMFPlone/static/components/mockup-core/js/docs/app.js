define([
  'jquery',
  'react',
  'backbone',
  'mockup-docs-view'
], function($, React, Backbone, AppView) {
  'use strict';

  var App = Backbone.Router.extend({
    routes: {
      '*id': 'openPage',
    },

    initialize: function(options) {
      this.options = options || {};
      this._view = new AppView({
        pages: this.options.pages,
        app: this
      });
      React.renderComponent(this._view, document.body);
      Backbone.history.start({ pushState: false });
    },

    openPage: function(page) {
      if (page === null) {
        page = this.options.defaultPage || 'index';
      }
      this._view.setState({ page: page });
    }
  });

  return App;
});
