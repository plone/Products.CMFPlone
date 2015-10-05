/* PreventDoubleSubmit pattern.
 *
 * Options:
 *    guardClassName(string): Class applied to submit button after it is clicked once. ('submitting')
 *    optOutClassName(string): Class used to opt-out a submit button from double-submit prevention. ('allowMultiSubmit')
 *    message(string): Message to be displayed when "opt-out" submit button is clicked a second time. ('You already clicked the submit button. Do you really want to submit this form again?')
 *
 * Documentation:
 *    # Example
 *
 *    {{ example-1 }}
 *
 * Example: example-1
 *    <form class="pat-preventdoublesubmit" onsubmit="javascript:return false;">
 *      <input type="text" value="submit this value please!" />
 *      <input class="btn btn-large btn-primary" type="submit" value="Single submit" />
 *      <input class="btn btn-large btn-primary allowMultiSubmit" type="submit" value="Multi submit" />
 *    </form>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'translate'
], function($, Base, _t) {
  'use strict';

  var PreventDoubleSubmit = Base.extend({
    name: 'preventdoublesubmit',
    trigger: '.pat-preventdoublesubmit',
    defaults: {
      message : _t('You already clicked the submit button. ' +
                'Do you really want to submit this form again?'),
      guardClassName: 'submitting',
      optOutClassName: 'allowMultiSubmit'
    },
    init: function() {
      var self = this;

      // if this is not a form just return
      if (!self.$el.is('form')) {
        return;
      }

      $(':submit', self.$el).click(function(e) {

        // mark the button as clicked
        $(':submit').removeAttr('clicked');
        $(this).attr('clicked', 'clicked');

        // if submitting and no opt-out guardClassName is found
        // pop up confirmation dialog
        if ($(this).hasClass(self.options.guardClassName) &&
              !$(this).hasClass(self.options.optOutClassName)) {
          return self._confirm.call(self);
        }

        $(this).addClass(self.options.guardClassName);
      });

    },

    _confirm: function(e) {
      return window.confirm(this.options.message);
    }

  });

  return PreventDoubleSubmit;

});
