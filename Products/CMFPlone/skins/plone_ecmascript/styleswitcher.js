// StyleSwitcher functions written by Paul Sowden
function setActiveStyleSheet(title, reset) {
    jQuery('link[rel*=style][title]').attr('disabled', true)
        .find('[title=' + title + ']').attr('disabled', false);
    if (reset) createCookie("wstyle", title, 365);
};

jQuery(function() {
    var style = readCookie("wstyle");
    if (style != null) setActiveStyleSheet(style, 0);
});
