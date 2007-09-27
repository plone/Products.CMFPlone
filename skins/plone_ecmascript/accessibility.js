function setBaseFontSize(fontsize, reset) {
    var body = $('body');
    if (reset == 1) {
        body.removeClass('smallText').removeClass('largeText');
        createCookie("fontsize", fontsize, 365);
    }
    body.addClass(fontsize);
};

$(function() {
    var fontsize = readCookie("fontsize");
    if (fontsize != null) {
        setBaseFontSize(fontsize, 0);
    }
});
