function setBaseFontSize($fontsize, $reset) {
    var $body = jq('body');
    if ($reset) {
        $body.removeClass('smallText').removeClass('largeText');
        createCookie("fontsize", $fontsize, 365);
    }
    $body.addClass($fontsize);
};

jq(function() {
    var $fontsize = readCookie("fontsize");
    if ($fontsize) setBaseFontSize($fontsize, 0);
});
