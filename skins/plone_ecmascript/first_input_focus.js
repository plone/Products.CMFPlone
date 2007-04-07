// Focus on error or element with tabindex==1
function setFocus(){
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    var $elements = cssQuery("form div.error input,"+
                             "form div.error textarea,"+
                             "form div.error select");
    console.log($elements);
    if ($elements.length > 0) {
        $elements[0].focus();
        return;
    }
    $elements = cssQuery("form input[tabindex=1],"+
                         "form textarea[tabindex=1],"+
                         "form select[tabindex=1]");
    console.log($elements);
    if ($elements.length > 0) {
        $elements[0].focus();
    }
}
if (typeof addDOMLoadEvent != "undefined") {
    addDOMLoadEvent(setFocus);
}
