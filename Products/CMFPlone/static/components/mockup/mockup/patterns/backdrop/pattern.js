/* Backdrop pattern.
 *
 * Options:
 *    zIndex(integer): z-index of backdrop element. (null)
 *    opacity(float): opacity level of backdrop element. (0.8)
 *    className(string): class name of backdrop element. ('backdrop')
 *    classActiveName(string): class name when backdrop is active. ('backdrop-active')
 *    closeOnEsc(boolean): should backdrop close when ESC key is pressed. (true)
 *    closeOnClick(boolean): should backdrop close when clicked on it. (true)
 *
 * Documentation:
 *    # TODO: we need example or this is not pattern :)
 *
 * Example: example-1
 *
 */


define([
  'jquery',
  'mockup-patterns-base'
], function($, Base) {
  'use strict';

  var Backdrop = Base.extend({
    name: 'backdrop',
    trigger: '.pat-backdrop',
    defaults: {
      zIndex: null,
      opacity: 0.8,
      className: 'plone-backdrop',
      classActiveName: 'plone-backdrop-active',
      closeOnEsc: true,
      closeOnClick: true
    },
    init: function() {
      var self = this;
      self.$backdrop = $('> .' + self.options.className, self.$el);
      if (self.$backdrop.size() === 0) {
        self.$backdrop = $('<div/>')
            .hide()
            .appendTo(self.$el)
            .addClass(self.options.className);
        if (self.options.zIndex !== null) {
          self.$backdrop.css('z-index', self.options.zIndex);
        }
      }
      if (self.options.closeOnEsc === true) {
        $(document).on('keydown', function(e, data) {
          if (self.$el.is('.' + self.options.classActiveName)) {
            if (e.keyCode === 27) {  // ESC key pressed
              self.hide();
            }
          }
        });
      }
      if (self.options.closeOnClick === true) {
        self.$backdrop.on('click', function() {
          if (self.$el.is('.' + self.options.classActiveName)) {
            self.hide();
          }
        });
      }
    },
    show: function() {
      var self = this;
      if (!self.$el.hasClass(self.options.classActiveName)) {
        self.emit('show');
        self.$backdrop.css('opacity', '0').show();
        self.$el.addClass(self.options.classActiveName);
        self.$backdrop.animate({ opacity: self.options.opacity }, 500);
        self.emit('shown');
      }
    },
    hide: function() {
      var self = this;
      if (self.$el.hasClass(self.options.classActiveName)) {
        self.emit('hide');
        self.$backdrop.animate({ opacity: '0' }, 500).hide();
        self.$el.removeClass(self.options.classActiveName);
        self.emit('hidden');
      }
    }
  });

  return Backdrop;

});
