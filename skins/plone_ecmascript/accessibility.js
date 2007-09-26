function setBaseFontSize(fontsize, reset) {
    var body = $('body');
    if (reset == 1) {
        body.removeClass('smallText');
        body.removeClass('largeText');
        createCookie("fontsize", fontsize, 365);
    }
    body.addClass(fontsize);
};

function initBaseFontSize() {
    var fontsize = readCookie("fontsize");
    if (fontsize != null) {
        setBaseFontSize(fontsize, 0);
    }
};
registerPloneFunction(initBaseFontSize);
