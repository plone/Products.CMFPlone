/*
  Provides globals setFullScreenMode, toggleFullScreenMode
  
  Deprecated. Not loaded by default in Plone 4.
*/

/*global createCookie:false, readCookie:false, window:false */

function setFullScreenMode(full) {
    if (full) {
        // set cookie
        jQuery('body').addClass('fullscreen');
        createCookie('fullscreenMode', '1');
        jQuery('#icon-full_screen').attr('src', 'fullscreencollapse_icon.png');
    } else {
        // unset cookie
        jQuery('body').removeClass('fullscreen');
        createCookie('fullscreenMode', '');
        jQuery('#icon-full_screen').attr('src', 'fullscreenexpand_icon.png');
    }
}

function toggleFullScreenMode() {
    setFullScreenMode(! jQuery('body').hasClass('fullscreen'));
}

jQuery(function($) {
    // test for a 'minimal=x' query parameter, where x == 1 means go fullscreen
    var minimal = $.grep(window.location.search.slice(1).split('&'),
                          function(a) { return a.indexOf('minimal=') === 0; });
    if (minimal.length && minimal[0].length > 8) {
        setFullScreenMode(minimal[0][8] === '1');
        return;
    }
    // based on cookie
    setFullScreenMode(readCookie('fullscreenMode') === '1');
});
