/* This is a stub, used by patterns that need compatibility with Mockup which
 * have i18n support.
 *
 * Eventually we might want to implement our own i18n functionality here (while
 * keeping compatibility with Mockup).
 *
 * Jed.js would be a good candidate. (http://slexaxton.github.io/Jed)
 */

define([], function() {
    return function translate (str) {
        return str;
    };
});
