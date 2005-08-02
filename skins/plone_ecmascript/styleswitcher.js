// StyleSwitcher functions written by Paul Sowden
function setActiveStyleSheet(title, reset) {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    var i, a, main;
    for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
        if (a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
            a.disabled = true;
            if (a.getAttribute("title") == title) {
                a.disabled = false;
            }
        }
    }
    if (reset == 1) {
        createCookie("wstyle", title, 365);
    }
};

function setStyle() {
    var style = readCookie("wstyle");
    if (style != null) {
        setActiveStyleSheet(style, 0);
    }
};
registerPloneFunction(setStyle);


