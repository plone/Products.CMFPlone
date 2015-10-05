define([
  'jquery',
  'backbone',
  'underscore',
  'mockup-ui-url/views/button',
  'text!mockup-patterns-structure-url/templates/selection_button.xml'
], function($, Backbone, _, ButtonView, tplButton) {
  'use strict';

  var SelectionButton = ButtonView.extend({
    collection: null,
    template: tplButton,
    initialize: function(options) {
      ButtonView.prototype.initialize.apply(this, [options]);
      var self = this;
      self.timeout = 0;
      if (this.collection !== null) {
        this.collection.on('add remove reset', function() {
          /* delay it */
          clearTimeout(self.timeout);
          self.timeout = setTimeout(function(){
            self.render();
            if (self.collection.length === 0) {
              self.$el.removeClass('active');
            }
          }, 50);
        }, this);
      }
    },
    serializedModel: function() {
      var obj = {icon: '', title: this.options.title, length: 0};
      if (this.collection !== null) {
        obj.length = this.collection.length;
      }
      return obj;
    }
  });

  return SelectionButton;
});
