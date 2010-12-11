// accessibility.js
// provides global function setBaseFontSize, which is used on the
// accessibility page to set small, normal or large type.
//
// font size is stored in a "fontsize" cookie, which is read on each pageload.

/*global createCookie, readCookie */

function setBaseFontSize($fontsize, $reset) {
    var $body = jQuery('body');
    if ($reset) {
        $body.removeClass('smallText').removeClass('largeText');
        createCookie("fontsize", $fontsize, 365);
    }
    $body.addClass($fontsize);
}

jQuery(function($) {
    var $fontsize = readCookie("fontsize");
    if ($fontsize) {
        setBaseFontSize($fontsize, 0);
    }
});
