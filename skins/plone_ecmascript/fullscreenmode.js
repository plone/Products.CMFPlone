function setFullScreenMode(full) {
    var body = $('body');

    if (full) {
        // set cookie
        $('body').addClass('fullscreen')
        createCookie('fullscreenMode', '1');
        $('#icon-full_screen').attr('src', 'fullscreencollapse_icon.gif');
    } else {
        // unset cookie
        $('body').removeClass('fullscreen')
        createCookie('fullscreenMode', '');
        $('#icon-full_screen').attr('src', 'fullscreenexpand_icon.gif');
    }
};

function toggleFullScreenMode() {
    setFullScreenMode(!$('body').hasClass('fullscreen'));
}

$(function() {
    // test for a 'minimal=x' query parameter, where x == 1 means go fullscreen
    minimal = jQuery.grep(window.location.search.slice(1).split('&'),
                          "a.indexOf('minimal=') == 0");
    if (minimal.length && minimal[0].length > 8) {
        setFullScreenMode(minimal[0][8] == '1');
        return;
    }
    // based on cookie
    setFullScreenMode(readCookie('fullscreenMode') == '1');
});
