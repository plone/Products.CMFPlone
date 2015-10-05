/* Formunloadalert pattern.
 *
 * Options:
 *    changingEvents(string): Events on which to check for changes (space-separated). ('change keyup paste')
 *    changingFields(string): Fields on which to check for changes (comma-separated). ('input,select,textarea,fileupload')
 *    message(string): Confirmation message to display when dirty form is being unloaded. (Discard changes? If you click OK, any changes you have made will be lost.)
 *
 * Documentation:
 *    # Example
 *
 *    {{ example-1 }}
 *
 * Example: example-1
 *    <form class="pat-formunloadalert" onsubmit="javascript:return false;">
 *      <input type="text" value="" />
 *      <select>
 *        <option value="1">value 1</option>
 *        <option value="2">value 2</option>
 *      </select>
 *      <input
 *        class="btn btn-large btn-primary"
 *        type="submit" value="Submit" />
 *      <br />
 *      <a href="/">Click here to go somewhere else</a>
 *    </form>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'translate'
], function ($, Base, _t) {
  'use strict';

  var FormUnloadAlert = Base.extend({
    name: 'formunloadalert',
    trigger: '.pat-formunloadalert',
    _changed : false,       // Stores a listing of raised changes by their key
    _suppressed : false,     // whether or not warning should be suppressed
    defaults: {
      message :  _t('Discard changes? If you click OK, ' +
                 'any changes you have made will be lost.'),
      // events on which to check for changes
      changingEvents: 'change keyup paste',
      // fields on which to check for changes
      changingFields: 'input,select,textarea,fileupload'
    },
    init: function () {
      var self = this;
      // if this is not a form just return
      if (!self.$el.is('form')) { return; }

      $(self.options.changingFields, self.$el).on(
        self.options.changingEvents,
        function (evt) {
          self._changed = true;
        }
      );

      var $modal = self.$el.parents('.plone-modal');
      if ($modal.size() !== 0) {
        $modal.data('pattern-modal').on('hide', function(e) {
          var modal = $modal.data('pattern-modal');
          if (modal) {
            modal._suppressHide = self._handleUnload.apply(self, e);
          }
        });
      } else {
        $(window).on('beforeunload', function(e) {
          return self._handleUnload(e);
        });
      }

      self.$el.on('submit', function(e) {
        self._suppressed = true;
      });

    },
    _handleUnload : function (e) {
      var self = this;
      if (self._suppressed) {
        self._suppressed = false;
        return undefined;
      }
      if (self._changed) {
        var msg = self.options.message;
        self._handleMsg(e,msg);
        $(window).trigger('messageset');
        return msg;
      }
    },
    _handleMsg:  function(e,msg) {
      (e || window.event).returnValue = msg;
    }
  });
  return FormUnloadAlert;

});
