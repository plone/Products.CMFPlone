function setBaseFontSize(fontsize, reset) {
    var body = cssQuery('body')[0];
    if (reset == 1) {
        removeClassName(body, 'smallText');
        removeClassName(body, 'largeText');
        createCookie("fontsize", fontsize, 365);
    }
    addClassName(body, fontsize);
};

function initBaseFontSize() {
    var fontsize = readCookie("fontsize");
    if (fontsize != null) {
        setBaseFontSize(fontsize, 0);
    }
};
registerPloneFunction(initBaseFontSize);
