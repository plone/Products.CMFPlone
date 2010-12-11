// StyleSwitcher functions written by Paul Sowden
// Deprecated; will be removed in Plone 5.

/*
  Provides global setActiveStyleSheet
*/

/*global createCookie:false, readCookie:false */

function setActiveStyleSheet(title, reset) {
    jQuery('link[rel*=style][title]').attr('disabled', true)
        .find('[title=' + title + ']').attr('disabled', false);
    if (reset) {
        createCookie("wstyle", title, 365);
    }
}

jQuery(function() {
    var style = readCookie("wstyle");
    if (style) {
        setActiveStyleSheet(style, 0);
    }
});
