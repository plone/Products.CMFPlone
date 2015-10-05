define([
  'jquery',
  'backbone',
  'underscore',
  'mockup-ui-url/views/base',
  'mockup-patterns-tooltip'
], function($, Backbone, _, BaseView, Tooltip) {
  'use strict';

  var ButtonView = BaseView.extend({
    tagName: 'a',
    className: 'btn',
    eventPrefix: 'button',
    context: 'default',
    idPrefix: 'btn-',
    attributes: {
      'href': '#'
    },
    extraClasses: [],
    tooltip: null,
    template: '<% if (icon) { %><span class="glyphicon glyphicon-<%= icon %>"></span><% } %> <%= title %>',
    events: {
      'click': 'handleClick'
    },
    initialize: function(options) {
      if (!options.id) {
        var title = options.title || '';
        options.id = title !== '' ? title.toLowerCase().replace(' ', '-') : this.cid;
      }
      BaseView.prototype.initialize.apply(this, [options]);

      this.on('disable', function() {
        this.disable();
      }, this);

      this.on('enable', function() {
        this.enable();
      }, this);

      this.on('render', function() {
        this.$el.attr('title', this.options.title || '');
        this.$el.attr('aria-label', this.options.title || this.options.tooltip || '');
        if (this.context !== null) {
          this.$el.addClass('btn-' + this.context);
        }
        _.each(this.extraClasses, function(klass){
          this.$el.addClass(klass);
        });

        if (this.tooltip !== null) {

          this.$el.attr('title', this.tooltip);
          var tooltipPattern = new Tooltip(this.$el);
          // XXX since tooltip triggers hidden
          // suppress so it plays nice with modals, backdrops, etc
          this.$el.on('hidden', function(e) {
            if (e.type === 'hidden') {
              e.stopPropagation();
            }
          });
        }
      }, this);
    },
    handleClick: function(e) {
      e.preventDefault();
      if (!this.$el.is('.disabled')) {
        this.uiEventTrigger('click', this, e);
      }
    },
    serializedModel: function() {
      return _.extend({'icon': '', 'title': ''}, this.options);
    },
    disable: function() {
      this.options.disabled = true;
      this.$el.addClass('disabled');
    },
    enable: function() {
      this.options.disabled = false;
      this.$el.removeClass('disabled');
    }
  });

  return ButtonView;
});
