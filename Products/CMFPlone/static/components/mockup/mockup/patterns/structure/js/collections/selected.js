define([
  'backbone',
  'mockup-patterns-structure-url/js/models/result'
], function(Backbone, Result) {
  'use strict';

  var SelectedCollection = Backbone.Collection.extend({
    model: Result,
    removeResult: function(model) {
      return this.removeByUID(model.uid());
    },
    removeByUID: function(uid) {
      var found = this.getByUID(uid);
      if (found) {
        this.remove(found);
      }
      return found;
    },
    getByUID: function(uid) {
      return this.findWhere({UID: uid});
    }
  });

  return SelectedCollection;
});

