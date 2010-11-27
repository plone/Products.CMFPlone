function setBaseFontSize($fontsize, $reset) {
    var $body = jQuery('body');
    if ($reset) {
        $body.removeClass('smallText').removeClass('largeText');
        createCookie("fontsize", $fontsize, 365);
    }
    $body.addClass($fontsize);
};

(function($) { $(function() {
        var $fontsize = readCookie("fontsize");
        if ($fontsize) setBaseFontSize($fontsize, 0);
}); })(jQuery);
