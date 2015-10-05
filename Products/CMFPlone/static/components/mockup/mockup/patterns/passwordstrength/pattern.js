/* Password strength pattern
 *
 * Options:
 *    zxcvbn(url): Location to load zxcvbn from. Defaults to cdnjs
 *
 * Documentation:
 *
 *    # Simple
 *
 *    {{ example-1 }}
 *
 *    # Custom zxcvbn location
 *
 *    {{ example-2 }}
 *
 * Example: example-1
 *   <input type="password" class="pat-passwordstrength" />
 *
 * Example: example-2
 *   <input type="password"
 *          class="pat-passwordstrength"
 *          data-pat-passwordstrength="zxcvbn: //moo.com/zxcvbn.js"
 *          />
 *
 */

define([
  'jquery',
  'mockup-patterns-base'
], function($, Base) {
  'use strict';
  function loadScript(src) {
       var s, i,
           scripts = document.getElementsByTagName('script');

       // Check script element doesn't already exist
       for (i = 0; i < scripts.length; i++) {
           if (scripts[i].src.indexOf(src) !== -1) {
               return;
           }
       }

       // If not, add it to page
       s = document.createElement('script');
       s.type = 'text/javascript';
       s.async = true;
       s.src = src;
       scripts[0].parentNode.insertBefore(s, scripts[0]);
  }

  function jsDiv() {
      return $(document.createElement('div'));
  }

  var PasswordStrength = Base.extend({
    name: 'passwordstrength',
    trigger: '.pat-passwordstrength',
    defaults: {
        zxcvbn: '//cdnjs.cloudflare.com/ajax/libs/zxcvbn/1.0/zxcvbn.js'
    },
    init: function () {
      var self = this,
          $pwfield = this.$el,
          $pwmeter = jsDiv().append([jsDiv(), jsDiv(), jsDiv(), jsDiv()]);

      function setLevel() {
          var score = 0;

          if (typeof window.zxcvbn !== 'function') {
              // No zxcvbn yet, try and load it
              loadScript(self.options.zxcvbn);
          } else if ($pwfield[0].value.length > 0) {
              // Run zxcvbn, supplying the value of any other widgets in the form
              score = Math.max(1, window.zxcvbn(
                  $pwfield[0].value,
                  [].map.call(
                      ($pwfield[0].form || { elements: [] }).elements,
                      function (inp) {
                          if (inp === $pwfield[0]) {
                            return null;
                          }
                          return inp.value || null;
                      }
                  ).filter(function (x) { return x; })
              ).score);
          }
          $pwmeter.attr('class', 'pat-passwordstrength-meter level-' + score);
      }

      $pwfield.after($pwmeter);
      $pwfield.on('keyup', function(e) {
          var timeoutId = 0;

          clearTimeout(timeoutId);
          timeoutId = setTimeout(setLevel, 500);
      });
      setLevel();
    }
  });

  return PasswordStrength;
});
