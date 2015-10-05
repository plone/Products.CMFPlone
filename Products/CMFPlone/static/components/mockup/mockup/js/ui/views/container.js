define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/base'
], function($, _, Backbone, BaseView) {
  'use strict';

  var Container = BaseView.extend({
    id: '',
    items: [],
    itemContainer: null,
    isOffsetParent: true,
    idPrefix: 'container-',
    render: function() {
      if (this.options.id) {
        this.$el.attr('id', this.idPrefix + this.options.id);
      }

      this.applyTemplate();

      this.renderItems();
      this.bindEvents();

      if (this.isOffsetParent) {
        this.$el.addClass('ui-offset-parent');
      }

      this.trigger('render', this);

      this.afterRender();

      this.$el.data('component', this);
      return this;
    },
    renderItems: function() {
      var $container;

      if (this.itemContainer !== null) {
        $container = $(this.itemContainer, this.$el);
        if ($container.length === 0) {
          throw 'Item Container element not found.';
        }
      } else {
        $container = this.$el;
      }
      _.each(this.items, function(view) {
        if (view.appendInContainer === true) {
          $container.append(view.render().$el);
        } else {
          view.render();
        }
      }, this);
    },
    bindEvents: function() {
      var self = this;
      _.each(this.items, function(view) {
        view.on('all', function() {
          var slice = [].slice;
          var eventName = arguments[0];
          var eventTarget;
          var newName = self.id !== '' ? self.id + '.' + eventName : eventName;
          if (arguments.length > 1) {
            eventTarget = arguments[1];
          }
          if (newName !== eventName) {
            var newArgs = slice.call(arguments, 0);
            newArgs[0] = newName;
            self.trigger.apply(self, newArgs);
          }
          if (eventTarget !== undefined && eventTarget.isUIView === true) {
            if (eventTarget.propagateEvent(eventName) === true) {
              self.trigger.apply(self, arguments);
            }
          }
        });
      });
    },
    get: function(id) {
      // Remove the recursive part because it was confusing if two children had the
      // same id
      return _.findWhere(this.items, {'id': id});
    },
    add: function(item) {
      if (item.id !== undefined && this.get(item.id)) {
        throw 'Another item with the same `id` already exists.';
      }
      this.items.push(item);
    }
  });

  return Container;
});
