/* Cookie Trigger pattern.
 *
 * Show a DOM element if browser cookies are disabled.
 *
 * Documentation:
 *
 *    {{ example-1 }}
 *
 * Example: example-1
 *    <div class="portalMessage error pat-cookietrigger">
 *      Cookies are not enabled. You must enable cookies before you can log in.
 *    </div>
 */

define([
  'jquery',
  'mockup-patterns-base'
], function ($, Base) {
  'use strict';

  var CookieTrigger = Base.extend({
    name: 'cookietrigger',
    trigger: '.pat-cookietrigger',

    isCookiesEnabled: function() {
      /* Test whether cookies are enabled by attempting to set a cookie
       * and then change its value set test cookie.
       */
      var c = "areYourCookiesEnabled=0";
      document.cookie = c;
      var dc = document.cookie;
      // cookie not set?  fail
      if (dc.indexOf(c) === -1) {
        return 0;
      }
      // change test cookie
      c = "areYourCookiesEnabled=1";
      document.cookie = c;
      dc = document.cookie;
      // cookie not changed?  fail
      if (dc.indexOf(c) === -1) {
        return 0;
      }
      // delete cookie
      document.cookie = "areYourCookiesEnabled=; expires=Thu, 01-Jan-70 00:00:01 GMT";
      return 1;
    },

    showIfCookiesDisabled: function() {
      /* Show the element on which this pattern is defined if cookies are
       * disabled.
       */
      if (this.isCookiesEnabled()) {
        this.$el.hide();
      } else {
        this.$el.show();
      }
    },

    init: function () {
      this.showIfCookiesDisabled();
    },
  });
  return CookieTrigger;
});
