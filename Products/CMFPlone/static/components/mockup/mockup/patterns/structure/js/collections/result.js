define([
  'underscore',
  'backbone',
  'mockup-patterns-structure-url/js/models/result',
  'backbone.paginator'
], function(_, Backbone, Result) {
  'use strict';

  var ResultCollection = Backbone.Paginator.requestPager.extend({
    model: Result,
    queryHelper: null, // need to set
    initialize: function(models, options) {
      this.options = options;
      this.url = options.url;
      this.queryParser = options.queryParser;
      this.queryHelper = options.queryHelper;
      Backbone.Paginator.requestPager.prototype.initialize.apply(this, [models, options]);
    },
    pager: function() {
      this.trigger('pager');
      Backbone.Paginator.requestPager.prototype.pager.apply(this, []);
    },
    paginator_core: {
      // the type of the request (GET by default)
      type: 'GET',
      // the type of reply (jsonp by default)
      dataType: 'json',
      url: function() {
        return this.url;
      }
    },
    paginator_ui: {
      // the lowest page index your API allows to be accessed
      firstPage: 1,
      // which page should the paginator start from
      // (also, the actual page the paginator is on)
      currentPage: 1,
      // how many items per page should be shown
      perPage: 15
    },
    server_api: {
      query: function() {
        return this.queryParser();
      },
      batch: function() {
        this.queryHelper.options.batchSize = this.perPage;
        return JSON.stringify(this.queryHelper.getBatch(this.currentPage));
      },
      attributes: function() {
        return JSON.stringify(this.queryHelper.options.attributes);
      }
    },
    parse: function (response, baseSortIdx) {
      if(baseSortIdx === undefined){
        baseSortIdx = 0;
      }
      this.totalRecords = response.total;
      var results = response.results;
      // XXX manually set sort order here since backbone will otherwise
      // do arbitrary sorting?
      _.each(results, function(item, idx) {
        item._sort = idx;
      });
      return results;
    },
    comparator: '_sort'
  });

  return ResultCollection;
});
