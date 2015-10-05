define([
  'jquery',
  'underscore',
  'backbone',
  'mockup-ui-url/views/container',
  'mockup-patterns-backdrop',
  'text!mockup-ui-url/templates/popover.xml',
], function($, _, Backbone, ContainerView, Backdrop, PopoverTemplate) {
  'use strict';

  var PopoverView = ContainerView.extend({
    tagName: 'div',
    className: 'popover',
    eventPrefix: 'popover',
    template: PopoverTemplate,
    content: null,
    title: null,
    triggerView: null,
    idPrefix: 'popover-',
    triggerEvents: {
      'button:click': 'toggle'
    },
    placement: 'bottom',
    events: {
    },
    opened: false,
    closeOnOutClick: true,
    appendInContainer: true,
    backdrop: undefined,
    $backdrop: null,
    useBackdrop: true,
    backdropOptions: {
      zIndex: '1009',
      opacity: '0.4',
      className: 'backdrop backdrop-popover',
      classActiveName: 'backdrop-active',
      closeOnEsc: false,
      closeOnClick: true
    },
    initialize: function(options) {
      ContainerView.prototype.initialize.apply(this, [options]);
      this.bindTriggerEvents();

      this.on('render', function() {
        this.$el.attr('role', 'tooltip').attr('aria-hidden', 'true');
        this.renderTitle();
        this.renderContent();
      }, this);
    },
    afterRender: function () {
    },
    getTemplateOptions: function(){
      return this.options;
    },
    renderTitle: function() {
      var title = this.title;
      if(typeof(title) === 'function'){
        title = title(this.getTemplateOptions());
      }
      this.$('.popover-title').empty().append(title);
    },
    renderContent: function() {
      this.$('.popover-content').empty().append(this.content(this.getTemplateOptions()));
    },
    bindTriggerEvents: function() {
      if (this.triggerView) {
        _.each(this.triggerEvents, function(func, event) {
          var method = this[func];
          if (!method) {
            $.error('Function not found.');
          }
          this.stopListening(this.triggerView, event);
          this.listenTo(this.triggerView, event, method);
        }, this);
      }
    },
    getPosition: function() {
      var $el = this.triggerView.$el;
      return $.extend({}, {
        width: $el[0].offsetWidth,
        height: $el[0].offsetHeight
      }, $el.offset());
    },
    show: function() {
      /* hide existing */
      $('.popover:visible').each(function(){
        var popover = $(this).data('component');
        if(popover){
          popover.hide();
        }
      });

      var pos = this.getPosition();
      var $tip = this.$el, tp, placement, actualWidth, actualHeight;

      placement = this.placement;

      $tip.css({ top: 0, left: 0 }).addClass('active');

      actualWidth = $tip[0].offsetWidth;
      actualHeight = $tip[0].offsetHeight;

      switch (placement) {
        case 'bottom':
          tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - actualWidth / 2};
          break;
        case 'top':
          tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2};
          break;
        case 'left':
          tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth};
          break;
        case 'right':
          tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width};
          break;
      }

      this.applyPlacement(tp, placement);

      this.setBackdrop();
      if (this.useBackdrop === true) {
        this.backdrop.show();
      }

      this.opened = true;

      if (this.triggerView) {
        this.triggerView.$el.addClass('active');
      }

      this.uiEventTrigger('show', this);
      this.$el.attr('aria-hidden', 'false');
    },
    applyPlacement: function(offset, placement) {
      var $el = this.$el,
        $tip = this.$el,
        width = $tip[0].offsetWidth,
        height = $tip[0].offsetHeight,
        actualWidth,
        actualHeight,
        delta,
        replace;

      $el.removeClass(placement);

      $el.offset(offset)
        .addClass(placement)
        .addClass('active');

      actualWidth = $tip[0].offsetWidth;
      actualHeight = $tip[0].offsetHeight;

      if (placement === 'top' && actualHeight !== height) {
        offset.top = offset.top + height - actualHeight;
        replace = true;
      }

      if (placement === 'bottom' || placement === 'top') {
        delta = 0;

        if (offset.left < 0) {
          delta = offset.left * -2;
          offset.left = 0;
          $el.removeClass(placement);
          $el.offset(offset).addClass(placement);
          actualWidth = $tip[0].offsetWidth;
          actualHeight = $tip[0].offsetHeight;
        }

        this.positionArrow(delta - width + actualWidth, actualWidth, 'left');

      } else {
        this.positionArrow(actualHeight - height, actualHeight, 'top');
      }

      if (replace) {
        $el.offset(offset);
      }
    },
    positionArrow: function(delta, dimension, position) {
      var $arrow = this.$('.arrow');
      $arrow.css(position, delta ? (50 * (1 - delta / dimension) + '%') : '');
    },
    hide: function() {
      this.opened = false;
      this.$el.removeClass('active');
      if (this.triggerView) {
        this.triggerView.$el.removeClass('active');
      }
      this.uiEventTrigger('hide', this);
      this.$el.attr('aria-hidden', 'true');
    },
    toggle: function(button, e) {
      if (this.opened) {
        this.hide();
      } else {
        this.show();
      }
    },
    setBackdrop: function() {
      if (this.useBackdrop === true && this.backdrop === undefined) {
        var self = this;
        this.$backdrop = this.$el.closest('.ui-backdrop-element');
        if (this.$backdrop.length === 0) {
          this.$backdrop = $('body');
        }

        this.backdrop = new Backdrop(this.$backdrop, this.backdropOptions);
        this.backdrop.$el.on('hidden.backdrop.patterns', function(e) {
          if (e.namespace === 'backdrop.patterns') {
            e.stopPropagation();
            if (self.opened === true) {
              self.hide();
            }
          }
        });
        this.on('popover:hide', function() {
          this.backdrop.hide();
        }, this);
      }
    }
  });

  return PopoverView;
});

