function toggleFullScreenMode() {
    var body = cssQuery('body')[0];
    if(document.getElementById('icon-full_screen')) {
    var fsicon = document.getElementById('icon-full_screen'); }

    if (hasClassName(body, 'fullscreen')) {
        // unset cookie
        removeClassName(body, 'fullscreen');
        createCookie('fullscreenMode', '');
        if(fsicon) { fsicon.src = 'fullscreenexpand_icon.gif'; }
    } else {
        // set cookie
        addClassName(body, 'fullscreen');
        createCookie('fullscreenMode', '1');
        if(fsicon) { fsicon.src = 'fullscreencollapse_icon.gif'; }
    }
};

function fullscreenModeLoad() {
    if(document.getElementById('icon-full_screen')) {
    var fsicon = document.getElementById('icon-full_screen'); }
    // based on cookie
    if (readCookie('fullscreenMode') == '1') {
        var body = cssQuery('body')[0];
        addClassName(body, 'fullscreen');
        if(fsicon) { fsicon.src = 'fullscreencollapse_icon.gif'; }
    }
};
registerPloneFunction(fullscreenModeLoad)
