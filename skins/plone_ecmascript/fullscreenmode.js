function toggleFullScreenMode() {
    var body = cssQuery('body')[0];

    if (hasClassName(body, 'fullscreen')) {
        // unset cookie
        removeClassName(body, 'fullscreen');
        createCookie('fullscreenMode', '');
    } else {
        // set cookie
        addClassName(body, 'fullscreen');
        createCookie('fullscreenMode', '1');
    }
};

function fullscreenModeLoad() {
    // based on cookie
    if (readCookie('fullscreenMode') == '1') {
        var body = cssQuery('body')[0];
        addClassName(body, 'fullscreen');
    }
};
registerPloneFunction(fullscreenModeLoad)
