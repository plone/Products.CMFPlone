function setFullScreenMode(fs) {
    var icon = document.getElementById('icon-full_screen');

    if (fs) {
        // set cookie
        addClassName(document.body, 'fullscreen');
        createCookie('fullscreenMode', '1');
        if(icon) { icon.src = 'fullscreencollapse_icon.gif'; }
    } else {
        // unset cookie
        removeClassName(document.body, 'fullscreen');
        createCookie('fullscreenMode', '');
        if(icon) { icon.src = 'fullscreenexpand_icon.gif'; }
    }
};

function toggleFullScreenMode() {
    setFullScreenMode(hasClassName(document.body, 'fullscreen') == false);
};

function fullscreenModeLoad() {
    // based on query string
    var queryparts = window.location.search.slice(1).split('&');
    for (var i=0; i<queryparts.length; i++) {
        var parts = queryparts[i].split('=');
        if (parts[0] == 'minimal' && parts[1] != null) {
            setFullScreenMode(parts[1] == '1');
            return;
        }
    }
    // based on cookie
    setFullScreenMode(readCookie('fullscreenMode') == '1');
};
registerPloneFunction(fullscreenModeLoad)
